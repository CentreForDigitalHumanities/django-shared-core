from django.core.files import File
from django.db import router
from django.db.models import ObjectDoesNotExist
from django.db.models.fields.related_descriptors import \
    ForeignKeyDeferredAttribute, ForwardManyToOneDescriptor


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

    def _create_file_wrapper(self, instance, file_obj):
        """Helper that creates a FileWrapper given a parent and a child
        instance"""
        file_wrapper = self.field.attr_class(
            child_instance=instance,
            file_instance=file_obj,
            field=self.field,
            name=file_obj.original_filename
        )
        # Register this FileWrapper as the wrapper on File
        file_obj.file = file_wrapper

        return file_wrapper

    def _create_file_instance(self):
        """Creates a brand-spanking new File instance (or the configured
        subclass)"""
        obj = self.field.remote_field.model.objects.create()
        obj.set_child_info_from_field(self.field)
        return obj

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
            if file_wrapper._removed:
                return None

            return file_wrapper
        except KeyError:
            # Try to fetch it from the DB instead
            file_obj = self.get_object(instance)

        # From this point on we are dealing with a fresh non-cached File object

        if file_obj is None and not self.field.null:
            raise self.RelatedObjectDoesNotExist(
                "%s has no %s." % (self.field.model.__name__, self.field.name)
            )

        # Create our wrapper
        file_wrapper = self._create_file_wrapper(instance, file_obj)
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

        if value._has_file_wrapper:  # NoQA
            # If the FileWrapper was previously marked for termination, we need
            # to save it now that we have assigned it again
            value.file._removed = False
            return value.file
        else:
            return self._create_file_wrapper(instance, value)

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

        # Mark this field for termination if we weren't given a file but it was
        # marked as changed, as that must mean the user wanted to clear the
        # field
        if not file and changed:
            return self._set_from_none(instance)

        # If this is an existing File, get the model
        if uuid:
            obj = self.field.remote_field.model.objects.get(uuid=uuid)
        # If not, create one if we did get a file to save
        elif file:
            obj = self._create_file_instance()
            # Set changed to true, as we are creating a new instance
            changed = True
        # If we also didn't get a file, just act if we received a None
        else:
            return self._set_from_none(instance)

        # Make sure we setup the DB side of things
        self._setup_db_state(instance, obj)

        # Re-use an existing wrapper if present
        if obj._has_file_wrapper:  # NoQA
            file_wrapper = obj.file
        elif self.field.is_cached(instance):
            file_wrapper = self.field.get_cached_value(instance)
        else:
            file_wrapper = self._create_file_wrapper(instance, obj)

        if file and changed:
            obj.original_filename = file.name
            file_wrapper.file = file
            file_wrapper._committed = False  # Mark the wrapper as need-to-save
            file_wrapper._removed = False  # One could set a new file after
            # setting the field to 'None', so we need to make sure the removed
            # flag from setting 'None' is removed (irony)

        return file_wrapper

    def _set_from_file_wrapper(self, instance, value):
        """Set this field's value from an existing FileWrapper

        The given file wrapper will override any existing in cache, but the
        cached wrapper will supplement any missing fields in the given wrapper
        """
        # If we have something in cache, try to set missing values from the
        # cache
        if self.field.is_cached(instance):
            cached = self.field.get_cached_value(instance)
            # If the cached value is in fact the same instance as the one we're
            # given, we skip this step
            if cached is not value:
                value.name = getattr(
                    value,
                    'name',
                    cached.name
                )
                value.child_instance = getattr(
                    value,
                    'child_instance',
                    cached.child_instance
                )
                value.file_instance = getattr(
                    value,
                    'file_instance',
                    cached.file_instance
                )
                value.field = getattr(
                    value,
                    'field',
                    cached.field
                )
                value._committed = False
        # Create a file instance if one isn't present
        if not value.file_instance:
            value.file_instance = self._create_file_instance()
            # It's a manually created FileWrapper as far as we know, so we
            # need to safe it at some point;
            value._committed = False
            value._removed = False

        self._setup_db_state(instance, value)

        # Make sure that all required fields are filled
        if not value.child_instance:
            value.child_instance = instance
        if not value.field:
            value.field = self.field

        return value

    def _set_from_file_like_object(self, instance, value):
        """Sets from a Django File object."""
        # If we have something in cache, add it to that wrapper
        if self.field.is_cached(instance):
            file_wrapper = self.field.get_cached_value(instance)
            file_wrapper.file = value
            file_wrapper._removed = False
            file_wrapper._committed = False

            return file_wrapper

        # If not, try to retrieve it from the DB or create a new DB obj if
        # it does not exist
        db_obj = self.get_object(instance)
        if not db_obj:
            db_obj = self._create_file_instance()

        self._setup_db_state(instance, db_obj)

        # Create a new wrapper and set the file
        file_wrapper = self._create_file_wrapper(instance, db_obj)
        file_wrapper.file = value
        file_wrapper._committed = False

        return

    def _set_from_none(self, instance):
        """Handles removing the current value by setting it to None."""
        # First, see if we have a cached value
        obj = self.field.get_cached_value(instance, None)

        # If not, try to retrieve one from the DB
        if obj is None:
            db_instance = self.get_object(instance)
            # If it's in the DB, create a wrapper for it
            if db_instance is not None:
                obj = self._create_file_wrapper(instance, db_instance)

        # If it's still not found, actually return None
        if obj is None:
            return None

        # If we have an object, mark it as 'removed' and return it
        # We don't actually remove the wrapper, as we need it's metadata to
        # properly remove everything when the model is saved. We can't delete
        # it now for two reasons:
        # 1) Deleting the File before dereferencing it in the child, we get
        #    integrity errors. The only way to avoid this is to actually save
        #    the child first, which brings us to 2:
        # 2) It's against normal Django behaviour to alter ANY data before
        #    calling .save() (or .remove() for that matter). Thus, we need to
        #    wait till the programmer expects things to change.
        obj._removed = True
        return obj
