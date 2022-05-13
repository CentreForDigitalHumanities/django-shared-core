from django.db import router
from django.db.models.fields.related_descriptors import \
    ForeignKeyDeferredAttribute, ForwardManyToOneDescriptor


class FileDescriptor(ForeignKeyDeferredAttribute):
    pass


class ForwardFileDescriptor(ForwardManyToOneDescriptor):

    def _create_file_proxy(self, instance, file_obj):
        file_proxy = self.field.attr_class(
            child_instance=instance,
            file_instance=file_obj,
            field=self.field,
            name=file_obj.original_filename
        )
        file_obj.file = file_proxy

        return file_proxy

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        try:
            return self.field.get_cached_value(instance)
        except KeyError:
            file_obj = self.get_object(instance)

        if file_obj is None and not self.field.null:
            raise self.RelatedObjectDoesNotExist(
                "%s has no %s." % (self.field.model.__name__, self.field.name)
            )

        file_proxy = self._create_file_proxy(instance, file_obj)

        self.field.set_cached_value(instance, file_proxy)

        return file_proxy

    def __set__(self, instance, value):
        if isinstance(value, tuple):
            return_value = self._set_from_tuple(instance, value)
        elif isinstance(
               value,
               self.field.remote_field.model._meta.concrete_model  # NoQA
           ):
            return_value = self._set_from_db(instance, value)
        elif isinstance(value, self.field.attr_class):
            return_value = self._set_from_file_obj(instance, value)
        else:
            raise ValueError(
                'Cannot assign "%r": "%s.%s" must be either a "%s" instance, '
                'a ProxyFile instance or a FileWidget tuple.'
                % (
                    value,
                    instance._meta.object_name,  # NoQA
                    self.field.name,
                    self.field.remote_field.model._meta.object_name,  # NoQA
                )
            )

        self.field.set_cached_value(instance, return_value)

        if return_value is None:

            for lh_field, rh_field in self.field.related_fields:
                setattr(instance, lh_field.attname, None)

    def _set_from_db(self, instance, value):
        value = self._setup_db_state(instance, value)

        if value._has_file_proxy:  # NoQA
            return value.file
        else:
            return self._create_file_proxy(instance, value)

    def _setup_db_state(self, instance, value):
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

    def _set_from_tuple(self, instance, value):
        file, uuid, changed = value
        # Remove this file model if we don't have a file but it was marked as
        # changed
        if not file and changed:
            return None

        # If this is an existing file, get the model
        if uuid:
            obj = self.field.remote_field.model.objects.get(uuid=uuid)
        # If not, then create one if we actually did get a file
        elif file:
            obj = self.field.remote_field.model.objects.create(
                app_name=self.field.model._meta.app_label,  # NoQA
                model_name=self.field.model._meta.object_name,  # NoQA
            )
        # If we also didn't get a file, just act if we received a None
        else:
            return None

        # Make sure we setup the DB side of things
        self._setup_db_state(instance, obj)

        if obj._has_file_proxy:  # NoQA
            file_proxy = obj.file
        else:
            file_proxy = self._create_file_proxy(instance, obj)

        if file and changed:
            obj.original_filename = file.name
            file_proxy.file = file

        return file_proxy

    def _set_from_file_obj(self, instance, value):
        if value.file_instance:
            self._setup_db_state(instance, value)
        else:
            value.file_instance = self.field.model.objects.create()

        if not value.child_instance:
            value.child_instance = instance
        if not value.field:
            value.field = self.field

        return value
