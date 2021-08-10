from django.db import models


class FileManager(models.Manager):

    def get_queryset_from_model(self, model):
        """Given a model, it will return a QS returning all files for the
        given model"""
        if not issubclass(model, models.Model):
            raise ValueError("Given model is not a Django model!")

        return self.get_queryset().filter(
            app_name=model._meta.app_label,  # NoQA
            model_name=model._meta.object_name,  # NoQA
        )

    def get_queryset_from_field(self, field):
        """Given a field, it will return a QS returning all files for the
        given field"""
        from uil.files.db import FileField
        if not issubclass(field, FileField):
            raise ValueError("Given field is not a FileField!")

        return self.get_queryset().filter(
            app_name=field.model._meta.app_label,  # NoQA
            model_name=field.model._meta.object_name,  # NoQA
            field_name=field.name,
        )
