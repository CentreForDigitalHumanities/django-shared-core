from django.apps import AppConfig


class FilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'uil.files'

    def ready(self):
        import uil.files.checks  # noQA, the import has side effects, linter!
        import uil.files.signals # noQA, same story