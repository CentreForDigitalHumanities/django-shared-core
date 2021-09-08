from django.core import checks, exceptions
from django.db import router
from django.db.models import ForeignObject, ManyToOneRel, CASCADE, SET_DEFAULT, \
    SET_NULL
from django.db.models.fields.related import RECURSIVE_RELATIONSHIP_CONSTANT
from django.db.models.query_utils import PathInfo
from django.db.models.signals import post_delete, post_save, pre_delete
from django.utils.translation import gettext_lazy as _

from .descriptors import FileDescriptor, ForwardFileDescriptor
from ..forms import fields
from .models import File
from .file_wrapper import FileWrapper


def _default_filename_generator(file_wrapper: FileWrapper):
    return file_wrapper.original_filename


class FileField(ForeignObject):
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
                 filename_generator: callable = None, **kwargs):
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
            related_name='+',  # No backward relations in uil.files.File pls
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

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_on_delete(),
            *self._check_unique(),
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

        # Not in this implementation of RelatedField
        if 'related_name' in kwargs:
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
            value = self.get_cached_value(instance, None)
            # If the cache contained a FileWrapper which is marked for
            # termination
            if value and value._removed:
                # Terminate this file
                value.delete()
                # And clear our cached value
                self.delete_cached_value(instance)

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
            # If so, we terminate this file!
            value = self.get_cached_value(instance, None)
            value.delete()

    def contribute_to_class(self, *args, **kwargs):
        super().contribute_to_class(*args, **kwargs)
        # Connect ourselves to some signals;
        # Fields really ought to have these methods themselves Django,
        # you already provide the pre_save method!
        post_save.connect(self.post_save, sender=self.model)
        pre_delete.connect(self.pre_delete, sender=self.model)
        post_delete.connect(self.post_delete, sender=self.model)

    def contribute_to_related_class(self, cls, related):
        pass  # not needed (otherwise the File class would get a lot of stuff
        # attached to it)

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
