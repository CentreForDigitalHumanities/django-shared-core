import io

from django.core.files import File
from django.db import  router
from django.db.models import ObjectDoesNotExist
from django.db.models.fields.related_descriptors import \
    ForeignKeyDeferredAttribute, ForwardManyToOneDescriptor, \
    ReverseManyToOneDescriptor
from django.utils.functional import cached_property

from uil.files.db.manager import create_tracked_file_manager
from uil.files.db.wrappers import FileWrapper, TrackedFileWrapper


class FileDescriptor(ForeignKeyDeferredAttribute):
    """FileDescriptor handles the {field_name}_id field of a FileField"""
    def __set__(self, instance, value):
        # Override of default implementation that does not clear the cache
        # when given None. This is needed as ForwardFileDescriptor handles None
        # in it's own way
        instance.__dict__[self.field.attname] = value


class ForwardFileDescriptor(ForwardManyToOneDescriptor):
    """FileDescriptor handles the {field_name}_ field of a FileField on the
    child (aka the model that has the field definition, parent would be the
    File model)."""

    def _create_file_wrapper(self, file_obj) -> FileWrapper:
        """Helper that creates a FileWrapper given a parent and a child
        instance        """
        return file_obj.get_file_wrapper(self.field)

    def _create_file_instance(self):
        """Creates a brand-spanking new File instance (or the configured
        subclass)"""
        return self.field.remote_field.model.objects.create()

    def get_object(self, instance):
        """Override get_object in order to handle non-existing File objects

        The default implementation does not need to worry about it, but we do
        (as we are hiding the fact that this is a ForeignKey relation)"""
        try:
            qs = self.get_queryset(instance=instance)
            return qs.get(self.field.get_reverse_related_filter(instance))
        except ObjectDoesNotExist:
            return None

    def __get__(self, instance, cls=None):
        """Retrieve the File object from cache, failing that from DB,
        and wrap it neatly in a FileWrapper"""
        # If we aren't given an instance, someone is calling it Class.field,
        # thus, we need to return the descriptor
        if instance is None:
            return self

        try:
            # See if we have it in cache, raises KeyError if not
            file_wrapper = self.field.get_cached_value(instance)

            # Act like we don't have this object if it is marked as removed
            # We actually keep it in cache, as we need it's metadata when saving
            # the child model. (Otherwise, we can't remove the File object from
            # the DB or the file from the disk when saving the new state).
            # The cache will be cleared once the file has been properly
            # disposed of
            if file_wrapper is None or file_wrapper._removed:
                return None

            return file_wrapper
        except KeyError:
            # Try to fetch it from the DB instead
            file_obj = self.get_object(instance)

        # From this point on we are dealing with a fresh non-cached File object

        if file_obj is None:
            if not self.field.null:
                raise self.RelatedObjectDoesNotExist(
                    "%s has no %s." % (self.field.model.__name__, self.field.name)
                )
            else:
                return None

        # Create our wrapper
        file_wrapper = file_obj.get_file_wrapper(self.field)
        # And cache it, saves some DB calls later!
        self.field.set_cached_value(instance, file_wrapper)

        return file_wrapper

    def __set__(self, instance, value):
        """Sets the value on the model instance from a variety of different
        input types

        1) Tuple - from our file widget.
        2) File instance - or any subclasses
        3) FileWrapper
        4) A Django File (derived) object
        5) None

        In all cases it will result in saving a FileWrapper, with 'None' being
        a special case that _can_ result in saving None, but not always.

        Please see the helper methods for detailed info on how they are handled
        """
        if isinstance(value, tuple):
            return_value = self._set_from_tuple(instance, value)
        elif isinstance(
               value,
               self.field.remote_field.model._meta.concrete_model  # NoQA
           ):
            return_value = self._set_from_db_instance(instance, value)
        elif isinstance(value, self.field.attr_class):
            return_value = self._set_from_file_wrapper(instance, value)
        elif isinstance(value, File):
            return_value = self._set_from_file_like_object(instance, value)
        elif value is None:
            return_value = self._set_from_none(instance)
        else:
            # We can't be completely inclusive :o
            raise ValueError(
                'Cannot assign "%r": "%s.%s" must be either a "%s" instance, '
                'a FileWrapper instance or a FileWidget tuple.'
                % (
                    value,
                    instance._meta.object_name,  # NoQA
                    self.field.name,
                    self.field.remote_field.model._meta.object_name,  # NoQA
                )
            )

        self.field.set_cached_value(instance, return_value)

        if return_value is None or return_value._removed:
            # If we got returned None, or a FileWrapper marked for deletion, we
            # need to clear the fields that the ORM uses to link objects.
            # (In other words, the {field_name}_id field)
            # If we don't, the ORM will get VERY confused and raise
            # IntegrityError(s)
            for lh_field, rh_field in self.field.related_fields:
                setattr(instance, lh_field.attname, None)

    def _setup_db_state(self, instance, value):
        """Sets some fields the ORM needs for DB operations. Taken verbatim
        from the base implementation."""
        if value is not None:
            if instance._state.db is None:  # NoQA
                instance._state.db = router.db_for_write(  # NoQA
                    instance.__class__,
                    instance=value
                )
            if value._state.db is None:  # NoQA
                value._state.db = router.db_for_write(  # NoQA
                    value.__class__,
                    instance=instance
                )
            if not router.allow_relation(value, instance):
                raise ValueError(
                    f'Cannot assign "{value}": the current database router '
                    f'prevents this relation.'
                )

        for lh_field, rh_field in self.field.related_fields:
            setattr(instance, lh_field.attname,
                    getattr(value, rh_field.attname))

        return value

    def _set_from_db_instance(self, instance, value):
        """Handles setting the value from a File object (or a subclass)

        It mostly just creates or updates a FileWrapper around it.
        """
        value = self._setup_db_state(instance, value)
        file_wrapper = value.get_file_wrapper(self.field)
        # If the FileWrapper was previously marked for termination, we need
        # to save it now that we have assigned it again
        file_wrapper._removed = False
        return file_wrapper

    def _set_from_tuple(self, instance, value):
        """Handles setting from the tuple returned from the Widget.
        The tuple has to have three values:

        file - None|File-like object - (almost always InMemoryUploadedFile)
        uuid - None|str|UUID - The UUID of the File. None indicates no File
               object exists yet
        changed - Boolean - True if the widget recorded indicates something
                  changed, may it be a clear or a (new) file
        """
        file, uuid, changed = value

        # If changed == False, return what we already have saved (if anything)
        if not changed:
            return self.__get__(instance)

        # Mark this field for termination if we weren't given a file but it was
        # marked as changed, as that must mean the user wanted to clear the
        # field
        if not file:
            return self._set_from_none(instance)

        # If there is an existing File, mark it to be removed
        # NOTE: it will only be marked as a candidate. The File object has final
        # say in whether it's actually deleted. (It might be referenced by a
        # different FileField).
        if uuid:
            old_obj = self.field.remote_field.model.objects.get(uuid=uuid)
            old_file_wrapper = old_obj.get_file_wrapper(self.field)
            old_file_wrapper._removed = True
            # Cache it, so the field can remove it later on save
            # The new FW will be set later in the chain, so this cached value
            # will not be seen as 'current'
            self.field.set_cached_value(instance, old_file_wrapper)

        # Create a new metadata object for the received file
        obj = self._create_file_instance()

        # Make sure we setup the DB side of things
        self._setup_db_state(instance, obj)

        file_wrapper = obj.get_file_wrapper(self.field, False)

        obj.original_filename = file.name
        file_wrapper.file = file
        file_wrapper._committed = False  # Mark the wrapper as need-to-save
        file_wrapper._removed = False  # Just to be safe. There _should_ be
        # no way this is not False...

        return file_wrapper

    def _set_from_file_wrapper(self, instance, value):
        """Set this field's value from an existing FileWrapper

        The given file wrapper will override any existing in cache, but the
        cached wrapper will supplement any missing fields in the given wrapper
        """
        # Get the current value, if there is any
        try:
            current_fw = self.__get__(instance)
        except self.RelatedObjectDoesNotExist:
            current_fw = None

        # See if we own this wrapper
        if self.field.in_cache(instance, value):
            # If it isn't the 'current' value, mark the current value to be
            # removed. (It's going to be overriden by an older version
            # apparently)
            if current_fw != value:
                current_fw._removed = True
            # Make sure we won't remove it
            value._removed = False
            # We don't need to do anything more; __set__ will ensure it's going
            # to be the current value
            return value

        # If we have a current FileWrapper, we need to mark it as deleted as
        # we are replacing it. We don't need to cache it, as __get__ would
        # have done that for us
        if current_fw and current_fw != value:
            current_fw._removed = True
        elif current_fw == value:
            value._removed = False

        # Create a file instance if one isn't present
        if not value.file_instance:
            value.file_instance = self._create_file_instance()
            # Make sure our new file_instance knows of this wrapper :)
            value.file_instance.set_file_wrapper(value, self.field)
            # It's a manually created FileWrapper as far as we know, so we
            # need to safe it at some point;
            value._committed = False
            # Also make sure we won't delete this
            value._removed = False
        # If we got handed a FileWrapper that is attached to a different field
        # we need to make a new wrapper for this field
        # This really shouldn't happen if this FW has a file_instance,
        # as you should get a FW from that file_instance (in other words,
        # the only reason you don't receive a FW with a file_instance is if a
        # programmer created an empty (non field-attached) FileWrapper)
        elif value.field != self.field:
            file = value.file
            value = value.file_instance.get_file_wrapper(self.field, False)
            value.file = file

        self._setup_db_state(instance, value.file_instance)

        return value

    def _set_from_file_like_object(self, instance, value):
        """Sets from a Django File object."""
        # If we have something in cache, mark it as obsolete
        if self.field.is_cached(instance):
            old_file_wrapper = self.field.get_cached_value(instance)
            old_file_wrapper._removed = True
        else:
            try:
                current_fw = self.__get__(instance)
                if current_fw is not None:
                    current_fw._removed = True
            except self.RelatedObjectDoesNotExist:
                pass

        db_obj = self._create_file_instance()
        file_wrapper = db_obj.get_file_wrapper(self.field, False)
        self._setup_db_state(instance, db_obj)
        # Create a new wrapper and set the file
        file_wrapper.file = value
        file_wrapper.original_filename = value.name
        file_wrapper._committed = False

        return file_wrapper

    def _set_from_none(self, instance):
        """Handles removing the current value by setting it to None."""
        # First, see if we have a value
        try:
            obj = self.__get__(instance)
            # If we got a result, mark it as to be removed
            if obj:
                obj._removed = True
        except self.RelatedObjectDoesNotExist:
            # If we get this exception, we are not allowed to set None because
            # the field does not allow it
            raise ValueError("Cannot set null if null=False")

        # If there is no value, actually return None
        if obj is None:
            return None

        # If we have an object, mark it as 'removed' and return it
        # We don't actually remove the wrapper, as we need it's metadata to
        # properly remove everything when the model is saved. We can't delete
        # it now for two reasons:
        # 1) When trying to delete the File before dereferencing it in the
        #    child, the FileWrapper will refuse to delete. If we set
        #    _removed=True, FileField will automagically clean up for us
        # 2) It's against normal Django behaviour to alter ANY data before
        #    calling .save() (or .remove() for that matter). Thus, we need to
        #    wait till the programmer expects things to change.
        obj._removed = True
        return obj


class TrackedFileDescriptor(ReverseManyToOneDescriptor):

    @property
    def through(self):
        # through is provided so that you have easy access to the through
        # model (Book.authors.through) for inlines, etc. This is done as
        # a property to ensure that the fully resolved value is returned.
        return self.rel.through

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        if self.field.is_cached(instance):
            return self.field.get_cached_value(instance)

        wrapper = self._create_wrapper(instance)
        self.field.set_cached_value(instance, wrapper)

        return wrapper

    def _create_wrapper(self, instance) -> TrackedFileWrapper:
        return self.field.attr_class(
            manager=self.related_manager_cls(instance),
            instance=instance,
            field=self.field,
        )

    @cached_property
    def related_manager_cls(self):
        related_model = self.rel.model

        return create_tracked_file_manager(
            related_model._default_manager.__class__,  # NoQA
            self.rel,
        )

    def _get_set_deprecation_msg_params(self):
        return (
            'tracked file field',
            self.field.name,
        )
