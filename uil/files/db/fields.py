from functools import partial

from django.core import checks, exceptions
from django.db import router
from django.db.models import ForeignObject, ForeignObjectRel, ManyToOneRel, \
    CASCADE, SET_DEFAULT, \
    SET_NULL
from django.db.models.fields.related import ManyToManyField, \
    RECURSIVE_RELATIONSHIP_CONSTANT, lazy_related_operation, resolve_relation
from django.db.models.query_utils import PathInfo
from django.db.models.signals import post_delete, post_save, pre_delete
from django.db.models.utils import make_model_tuple
from django.dispatch import receiver
from django.forms import ModelMultipleChoiceField
from django.utils.hashable import make_hashable
from django.utils.translation import gettext_lazy as _
from uil.core.collections import IndexedOrderedSet

from .descriptors import FileDescriptor, ForwardFileDescriptor, \
    TrackedFileDescriptor
from ..forms import fields
from .models import BaseFile, File
from .wrappers import FileWrapper, TrackedFileWrapper

NOT_PROVIDED = object()


class FileFieldCacheMixin:
    """Provide an API for working with the model's fields value cache.

    This is a modified version of Django's FieldCacheMixin, which keeps track
    of the old """

    set_cls = IndexedOrderedSet

    def get_cache_name(self):
        raise NotImplementedError

    def get_cached_value(self, instance, default=NOT_PROVIDED, all=False):
        cache_name = self.get_cache_name()
        try:
            if all:
                return instance._state.fields_cache[cache_name]
            return instance._state.fields_cache[cache_name][-1]
        except (KeyError, IndexError):
            if all:
                return self.set_cls()
            if default is NOT_PROVIDED:
                raise KeyError
            return default

    def is_cached(self, instance):
        return self.get_cache_name() in instance._state.fields_cache and \
               len(instance._state.fields_cache[self.get_cache_name()]) > 0

    def in_cache(self, instance, value):
        return self.get_cache_name() in instance._state.fields_cache and \
               value in instance._state.fields_cache[self.get_cache_name()]

    def set_cached_value(self, instance, value, clear=False):
        if self.get_cache_name() not in instance._state.fields_cache or clear:
            instance._state.fields_cache[self.get_cache_name()] = self.set_cls()

        # If this value is already cached, we need to remove it before adding it
        # Otherwise, the value wouldn't be seen as the newest value (which
        # would cause get_cached_value to incorrectly return a different value)
        if self.in_cache(instance, value):
            self.delete_value_from_cache(instance, value)

        instance._state.fields_cache[self.get_cache_name()].add(value)

    def delete_value_from_cache(self, instance, value):
        if self.in_cache(instance, value):
            instance._state.fields_cache[self.get_cache_name()].remove(value)

    def clear_cache(self, instance):
        instance._state.fields_cache[self.get_cache_name()] = self.set_cls()

    def delete_cached_value(self, instance):
        # A hack around Django's behaviour. Django wants to clear the cache
        # if one swaps in a different related object to make sure the cache
        # doesn't contain an old value.
        # However, we handle this differently (as we keep track of old values
        # for housecleaning). Thus, we simply don't implement this specific
        # method and use one of the two above
        pass


def _default_filename_generator(file_wrapper: FileWrapper):
    return file_wrapper.original_filename


class FileField(FileFieldCacheMixin, ForeignObject):
    """A replacement for Django's FileField. To the programmer, a File-like
    object is exposed which they can use to interact with the files.

    The main advantages over Django's FileField are:

    - If a file is removed from a model, it's actually also removed from disk
      automatically. Django's version leaves it where it is, taking up space
    - Files are not stored on disk using their original filename, an UUID is
      used instead as the filename. This makes guessing filenames next to
      impossible, providing a (small) layer of security.
    - In addition, by default this system will store files in a non-web facing
      location. (Or at least it should be). Accessing these files should be done
      through a download view, allowing the programmer to add permission checks.

    Under the hood, it's actually a modified ForeignKey to (a subclass of)
    File, which keeps track of the metadata. A custom descriptor is then used to
    wrap it in a FileWrapper instance, which provides a File-like interface and
    (alongside the descriptor and this field) handles the complicated DB
    interactions.
    """
    descriptor_class = FileDescriptor
    # Field flags
    many_to_many = False
    many_to_one = True
    one_to_many = False
    one_to_one = False

    forward_related_accessor_class = ForwardFileDescriptor
    rel_class = ManyToOneRel
    attr_class = FileWrapper

    empty_strings_allowed = False
    default_error_messages = {
        'invalid': _(
            '%(model)s instance with %(field)s %(value)r does not exist.')
    }
    description = _("Foreign Key (type determined by related field)")

    def __init__(self, to=None, on_delete=None, to_field=None, db_constraint=True,
                 filename_generator: callable = None, url_pattern: str = None,
                 **kwargs):
        """

        :param to: A File-like model.
        :param on_delete: See Django docs for ForeignKey
        :param to_field: The field on File one should link to. Only change
                         this when using a different model in 'to' please
        :param db_constraint: See Django docs for ForeignKey
        :param filename_generator: A callable which, given a FileWrapper,
                                   will return a name for the file. Note that
                                   this isn't saved anywhere! Changing the
                                   callable will change the name of all
                                   existing files
        :param kwargs: See Django docs for ForeignKey
        """
        if to is None:
            to = File
        if on_delete is None:
            on_delete = CASCADE

        if filename_generator is None:
            filename_generator = _default_filename_generator
        self.filename_generator = filename_generator

        try:
            to._meta.model_name  # NoQA
        except AttributeError:
            assert isinstance(to, str), (
                    "%s(%r) is invalid. First parameter to ForeignKey must be "
                    "either a model, a model name, or the string %r" % (
                        self.__class__.__name__, to,
                        RECURSIVE_RELATIONSHIP_CONSTANT,
                    )
            )
        else:
            # For backwards compatibility purposes, we need to *try* and set
            # the to_field during FK construction. It won't be guaranteed to
            # be correct until contribute_to_class is called. Refs #12190.
            to_field = to_field or (to._meta.pk and to._meta.pk.name)
        if not callable(on_delete):
            raise TypeError('on_delete must be callable.')

        kwargs['rel'] = self.rel_class(
            self, to, to_field,
            # Ensure unique related name by using the id of this field
            # Should only be used by dynamic code, so the name does not matter
            # as much as avoiding conflicts in said name
            # the x_ prefix is mostly because Python doesn't allow numeric
            # variable names
            related_name=f"FF_{id(self)}",
            related_query_name=None,
            limit_choices_to=None,
            parent_link=False,
            on_delete=on_delete,
        )
        kwargs.setdefault('db_index', True)

        super().__init__(
            to,
            on_delete,
            from_fields=[RECURSIVE_RELATIONSHIP_CONSTANT],
            to_fields=[to_field],
            **kwargs,
        )
        self.db_constraint = db_constraint
        self.url_pattern = url_pattern

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_on_delete(),
            *self._check_unique(),
            *self._check_attr_class_subclass(),
            *self._check_basefile_subclass(),
            *self._check_file_subclass(),
        ]

    def _check_on_delete(self):
        on_delete = getattr(self.remote_field, 'on_delete', None)
        if on_delete == SET_NULL and not self.null:
            return [
                checks.Error(
                    'Field specifies on_delete=SET_NULL, but cannot be null.',
                    hint=('Set null=True argument on the field, or change the '
                          'on_delete rule.'),
                    obj=self,
                    id='fields.E320',
                )
            ]
        elif on_delete == SET_DEFAULT and not self.has_default():
            return [
                checks.Error(
                    ('Field specifies on_delete=SET_DEFAULT, but has no '
                     'default value.'),
                    hint='Set a default value, or change the on_delete rule.',
                    obj=self,
                    id='fields.E321',
                )
            ]
        else:
            return []

    def _check_unique(self, **kwargs):
        return [
            checks.Warning(
                ('Setting unique=True on a ForeignKey has the same effect as '
                 'using a OneToOneField.'),
                hint=('ForeignKey(unique=True) is usually better served by a '
                      'OneToOneField.'),
                obj=self,
                id='fields.W342',
            )
        ] if self.unique else []

    def _check_attr_class_subclass(self):
        return [
            checks.Warning(
                ('The `attr_class` value is not a subclass of '
                 'uil.files.db.FileWrapper'),
                hint=('Please ensure this wrapper implements the same API as '
                      'FileWrapper'),
                obj=self,
                id='uil.files.W002',
            )
        ] if not issubclass(self.attr_class, FileWrapper) else []

    def _check_file_subclass(self):
        return [
            checks.Error(
                ('The `to` parameter value is a subclass of '
                 'uil.files.db.File; you are not allowed to subclass File'),
                hint=('If you want to use a custom File model, '
                      'use uil.files.db.BaseFile as your base instead.'),
                obj=self,
                id='uil.files.E002',
            )
        ] if issubclass(self.remote_field.model, File) and \
             self.remote_field.model != File \
            else []

    def _check_basefile_subclass(self):
        return [
            checks.Warning(
                ('The `to` parameter value is not a subclass of '
                 'uil.files.db.BaseFile'),
                hint=('Please ensure this model implements the same API as '
                      'File'),
                obj=self,
                id='uil.files.W003',
            )
        ] if not issubclass(self.remote_field.model, BaseFile) else []

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['to_fields']
        del kwargs['from_fields']
        # Handle the simpler arguments
        if self.db_index:
            del kwargs['db_index']
        else:
            kwargs['db_index'] = False
        if self.db_constraint is not True:
            kwargs['db_constraint'] = self.db_constraint

        # Make sure we don't actually return an auto-generated related_name,
        # as those change every time Python starts up
        if 'related_name' in kwargs and kwargs['related_name'].startswith(
                'FF'
        ):
            del kwargs['related_name']
        if 'related_query_name' in kwargs:
            del kwargs['related_query_name']

        if self.filename_generator is not None:
            kwargs['filename_generator'] = self.filename_generator

        # Rel needs more work.
        to_meta = getattr(self.remote_field.model, "_meta", None)
        if self.remote_field.field_name and (
                not to_meta or (
                to_meta.pk and
                self.remote_field.field_name != to_meta.pk.name
        )
        ):
            kwargs['to_field'] = self.remote_field.field_name
        return name, path, args, kwargs

    def to_python(self, value):
        return self.target_field.to_python(value)

    @property
    def target_field(self):
        return self.foreign_related_fields[0]

    def get_reverse_path_info(self, filtered_relation=None):
        """Get path from the related model to this field's model."""
        opts = self.model._meta
        from_opts = self.remote_field.model._meta
        return [PathInfo(
            from_opts=from_opts,
            to_opts=opts,
            target_fields=(opts.pk,),
            join_field=self.remote_field,
            m2m=not self.unique,
            direct=False,
            filtered_relation=filtered_relation,
        )]

    def validate(self, value, model_instance):
        if self.remote_field.parent_link:
            return
        super().validate(value, model_instance)
        if value is None:
            return

        using = router.db_for_read(self.remote_field.model,
                                   instance=model_instance)
        qs = self.remote_field.model._base_manager.using(using).filter(
            **{
                self.remote_field.field_name: value
            }
        )
        qs = qs.complex_filter(self.get_limit_choices_to())
        if not qs.exists():
            raise exceptions.ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={
                    'model': self.remote_field.model._meta.verbose_name,
                    'pk':    value,
                    'field': self.remote_field.field_name,
                    'value': value,
                },  # 'pk' is included for backwards compatibility
            )

    def resolve_related_fields(self):
        related_fields = super().resolve_related_fields()
        for from_field, to_field in related_fields:
            if to_field and \
                    to_field.model != self.remote_field.model._meta.concrete_model:
                raise exceptions.FieldError(
                    "'%s.%s' refers to field '%s' which is not local to model "
                    "'%s'." % (
                        self.model._meta.label,
                        self.name,
                        to_field.name,
                        self.remote_field.model._meta.concrete_model._meta.label,
                    )
                )
        return related_fields

    def get_attname(self):
        return '%s_id' % self.name

    def get_attname_column(self):
        attname = self.get_attname()
        column = self.db_column or attname
        return attname, column

    def get_default(self):
        """Return the to_field if the default value is an object."""
        field_default = super().get_default()
        if isinstance(field_default, self.remote_field.model):
            return getattr(field_default, self.target_field.attname)
        return field_default

    def get_db_prep_save(self, value, connection):
        if value is None or \
                (value == '' and (
                        not self.target_field.empty_strings_allowed or
                        connection.features.interprets_empty_strings_as_nulls)
                ):
            return None
        else:
            return self.target_field.get_db_prep_save(value,
                                                      connection=connection)

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.target_field.get_db_prep_value(value, connection, prepared)

    def get_prep_value(self, value):
        return self.target_field.get_prep_value(value)

    def pre_save(self, model_instance, add):
        """Make sure we save our file when saving the model this field is
        attached to"""
        ret = super().pre_save(model_instance, add)

        file = getattr(model_instance, self.name, None)
        # If we have a file and it's marked as not-saved (committed)
        if file is not None and not file._committed:
            # Commit the file to storage prior to saving the model
            # This will also save the File instance
            file.save()

        return ret

    def post_save(self, sender, instance, created, **kwargs):
        """Handle deletion of a file"""
        # If we have something in cache
        if self.is_cached(instance):
            # Get all values
            # The cache can contain multiple values, in which case all but
            # the last of them should be marked for deletion
            values = self.get_cached_value(instance, all=True)
            for value in values:
                # If this value is marked for removal, delete :D
                # Note: This might not actually delete the file, it might be
                # referenced by a different FileField, in which case
                # value.delete() will simple stop execution
                if value is not None and value._removed:
                    # Terminate this file
                    value.delete()
            # And clear our cached value
            self.clear_cache(instance)

    def pre_delete(self, sender, instance, **kwargs):
        # When our model is deleted, we need to remove all linked File objects
        # as well. As a File can exist without a model linking to it,
        # the DB/ORM won't do this automatically for us.
        # Additionally, we cannot remove our files first (as the
        # to-be-deleted instance is still referencing these files). Thus,
        # we simply force our file into the cache if it exists so we can delete
        # it after the instance is deleted.
        getattr(instance, self.name, None)

    def post_delete(self, sender, instance, **kwargs):
        # When our model was deleted, we should see if our cache contains files
        # that need to be deleted
        if self.is_cached(instance):
            value = self.get_cached_value(instance, None)
            num_references = value.file_instance._num_child_instances
            # Delete the File if no other object is referencing it
            if value is not None and num_references == 0:
                value.delete()

    def contribute_to_class(self, *args, **kwargs):
        super().contribute_to_class(*args, **kwargs)
        # Connect ourselves to some signals;
        # Fields really ought to have these methods themselves Django,
        # you already provide the pre_save method!
        post_save.connect(self.post_save, sender=self.model)
        pre_delete.connect(self.pre_delete, sender=self.model)
        post_delete.connect(self.post_delete, sender=self.model)

    def formfield(self, *, using=None, **kwargs):
        if isinstance(self.remote_field.model, str):
            raise ValueError("Cannot create form field for %r yet, because "
                             "its related model %r has not been loaded yet" %
                             (self.name, self.remote_field.model))

        return super().formfield(**{
            'form_class': fields.FileField,
            'max_length': self.max_length,
            'queryset':   self.remote_field.model._default_manager.using(using),
            **kwargs,
        })

    def db_check(self, connection):
        return []

    def db_type(self, connection):
        return self.target_field.rel_db_type(connection=connection)

    def db_parameters(self, connection):
        return {
            "type":  self.db_type(connection),
            "check": self.db_check(connection)
        }

    def convert_empty_strings(self, value, expression, connection):
        if (not value) and isinstance(value, str):
            return None
        return value

    def get_db_converters(self, connection):
        converters = super().get_db_converters(connection)
        if connection.features.interprets_empty_strings_as_nulls:
            converters += [self.convert_empty_strings]
        return converters

    def get_col(self, alias, output_field=None):
        if output_field is None:
            output_field = self.target_field
            while isinstance(output_field, FileField):
                output_field = output_field.target_field
                if output_field is self:
                    raise ValueError('Cannot resolve output_field.')
        return super().get_col(alias, output_field)

    def get_cache_name(self):
        return self.name


def create_tracked_file_intermediary_model(field, cls, file_kwargs: dict):
    from django.db import models

    def set_managed(model, related, through):
        through._meta.managed = model._meta.managed or related._meta.managed

    to_model = resolve_relation(cls, field.remote_field.model)
    name = '%s_%s' % (cls._meta.object_name, field.name)
    lazy_related_operation(set_managed, cls, to_model, name)

    to = make_model_tuple(to_model)[1]
    from_ = cls._meta.model_name

    meta = type('Meta', (), {
        'db_table': field._get_m2m_db_table(cls._meta),
        'auto_created': cls,
        'app_label': cls._meta.app_label,
        'db_tablespace': cls._meta.db_tablespace,
        'unique_together': (from_, to),
        'verbose_name': _('%(from)s-%(to)s relationship') % {'from': from_, 'to': to},
        'verbose_name_plural': _('%(from)s-%(to)s relationships') % {'from': from_, 'to': to},
        'apps': field.model._meta.apps,
    })
    # Construct and return the new class.
    new_cls = type(name, (models.Model,), {
        'Meta': meta,
        '__module__': cls.__module__,
        from_: models.ForeignKey(
            cls,
            related_name='%s+' % name,
            db_tablespace=field.db_tablespace,
            db_constraint=field.remote_field.db_constraint,
            on_delete=CASCADE,
        ),
        to: FileField(
            to=to_model,
            db_tablespace=field.db_tablespace,
            db_constraint=field.remote_field.db_constraint,
            on_delete=CASCADE,
            **file_kwargs
        ),
        'current': models.BooleanField(
            default=False
        )
    })

    @receiver(pre_delete, sender=cls)
    def cascade_file_m2m_delete(sender, instance, **kwargs):
        """
        Django does not propagate m2m deletion to the other side of the
        relation (as in most cases, it's not needed or wanted). However,
        in our case we actually want to delete the other side's objects as
        well. Otherwise, we'd get files that do not belong to any other model,
        which at best is a waste of space and at worst an AVG violation.

        The easiest method to do this, is just to attach a signal listener on
        the parent model and manually delete the other side. (Trust me,
        this is by far the easiest!)

        As we need to listen to the model we try to link to files, we cannot
        create this signal receiver in the signals file. Thus, we attach it
        right after creating the linking model.
        """
        # `field` comes from the method containing this method
        # Is used to retrieve the right wrapper by it's owner field's
        # accessor name
        wrapper = getattr(
            instance,
            field.attname,
            None,
        )

        # Should not really happen... *crosses fingers**
        if wrapper:
            for file in wrapper.all:
                file.delete()

    return new_cls


class TrackedFileRel(ForeignObjectRel):
    """
    Used by ManyToManyField to store information about the relation.

    ``_meta.get_fields()`` returns this class to provide access to the field
    flags for the reverse relation.
    """

    def __init__(self, field, to, related_name=None, related_query_name=None,
                 limit_choices_to=None, db_constraint=True):
        super().__init__(
            field, to,
            related_name=related_name,
            related_query_name=related_query_name,
            limit_choices_to=limit_choices_to,
        )

        self.through = None
        self.through_fields = None

        self.symmetrical = False
        self.db_constraint = db_constraint

    @property
    def identity(self):
        return super().identity + (
            self.through,
            make_hashable(self.through_fields),
            self.db_constraint,
        )

    def get_related_field(self):
        """
        Return the field in the 'to' object to which this relationship is tied.
        Provided for symmetry with ManyToOneRel.
        """
        opts = self.through._meta
        for field in opts.fields:
            rel = getattr(field, 'remote_field', None)
            if rel and rel.model == self.model:
                break

        # Disabled linter warning (which complains field is not always set)
        # as the for loop above _should_ always find the right field. If not,
        # this method isn't the problem ;)
        return field.foreign_related_fields[0] # NoQA;


class TrackedFileField(ManyToManyField):

    rel_class = TrackedFileRel
    attr_class = TrackedFileWrapper

    description = _("File field with history tracking")

    def __init__(self, to=None, related_name=None, related_query_name=None,
                 limit_choices_to=None, file_kwargs: dict = None,
                 db_constraint=True, db_table=None,
                 swappable=True, url_pattern: str = None, **kwargs):
        if to is None:
            to = File
        if file_kwargs is None:
            file_kwargs = {}

        self.url_pattern = url_pattern
        file_kwargs['url_pattern'] = url_pattern

        if related_name is None:
            related_name = f"TFF_{id(self)}"

        # Use the same related name if none was provided; makes debugging a tad
        # more easier as one can see the related is actually from a TFF
        if 'related_name' not in file_kwargs:
            file_kwargs['related_name'] = related_name

        try:
            to._meta
        except AttributeError:
            assert isinstance(to, str), (
                    "%s(%r) is invalid. First parameter to ManyToManyField must"
                    " be either a model, a model name, or the string %r" %
                    (self.__class__.__name__, to,
                     RECURSIVE_RELATIONSHIP_CONSTANT)
            )

        kwargs['rel'] = self.rel_class(
            self, to,
            related_name=related_name,
            related_query_name=related_query_name,
            limit_choices_to=limit_choices_to,
            db_constraint=db_constraint,
        )
        self.has_null_arg = 'null' in kwargs

        # Skip over ManyToMany's init
        super(ManyToManyField, self).__init__(**kwargs)

        self.db_table = db_table
        self.swappable = swappable
        self.file_kwargs = file_kwargs

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        # We don't have these parameters
        if 'through' in kwargs:
            del kwargs['through']
        if 'symmetrical' in kwargs:
            del kwargs['symmetrical']
        if 'through_fields' in kwargs:
            del kwargs['through_fields']

        # Make sure we don't actually return an auto-generated related_name,
        # as those change every time Python starts up
        if 'related_name' in kwargs and kwargs['related_name'].startswith(
                'TFF'
        ):
            del kwargs['related_name']

        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, **kwargs):
        if self.remote_field.is_hidden():
            # If the backwards relation is disabled, replace the original
            # related_name with one generated from the m2m field name. Django
            # still uses backwards relations internally and we need to avoid
            # clashes between multiple m2m fields with related_name == '+'.
            self.remote_field.related_name = '_%s_%s_%s_+' % (
                cls._meta.app_label,
                cls.__name__.lower(),
                name,
            )

        # Skip over ManyToMany's contribute_to_class
        super(ManyToManyField, self).contribute_to_class(cls, name, **kwargs)

        # The intermediate m2m model is not auto created if:
        #  1) NullPointerException
        #  2) The class owning the m2m field is abstract.
        #  3) The class owning the m2m field has been swapped out.
        if not cls._meta.abstract and not cls._meta.swapped:
            self.remote_field.through = create_tracked_file_intermediary_model(
                self,
                cls,
                self.file_kwargs,
            )

        # Add the descriptor for the m2m relation.
        setattr(
            cls,
            self.name,
            TrackedFileDescriptor(self.remote_field)
        )

        # Set up the accessor for the m2m table name for the relation.
        self.m2m_db_table = partial(self._get_m2m_db_table, cls._meta)

    def contribute_to_related_class(self, cls, related):
        # Set up the accessors for the column names on the m2m table.
        self.m2m_column_name = partial(self._get_m2m_attr, related, 'column')
        self.m2m_reverse_name = partial(self._get_m2m_reverse_attr, related, 'column')

        self.m2m_field_name = partial(self._get_m2m_attr, related, 'name')
        self.m2m_reverse_field_name = partial(self._get_m2m_reverse_attr, related, 'name')

        get_m2m_rel = partial(self._get_m2m_attr, related, 'remote_field')
        self.m2m_target_field_name = lambda: get_m2m_rel().field_name
        get_m2m_reverse_rel = partial(self._get_m2m_reverse_attr, related, 'remote_field')
        self.m2m_reverse_target_field_name = lambda: get_m2m_reverse_rel().field_name


    def formfield(self, *, using=None, **kwargs):
        defaults = {
            'form_class': ModelMultipleChoiceField,
            'queryset': self.remote_field.model._default_manager.using(using),
            **kwargs,
        }
        # If initial is passed in, it's a list of related objects, but the
        # MultipleChoiceField takes a list of IDs.
        if defaults.get('initial') is not None:
            initial = defaults['initial']
            if callable(initial):
                initial = initial()
            defaults['initial'] = [i.pk for i in initial]
        return super().formfield(**defaults)
