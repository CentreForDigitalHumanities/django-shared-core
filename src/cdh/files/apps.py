from django.apps import AppConfig


class FilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cdh.files'

    def ready(self):
        import cdh.files.checks  # noQA, the import has side effects, linter!
        import cdh.files.signals # noQA, same story
