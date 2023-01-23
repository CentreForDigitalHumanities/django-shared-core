from django.apps import AppConfig


class IntegrationPlatformConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cdh.integration_platform'

    def ready(self):
        import cdh.integration_platform.checks  # noQA, the import has side effects, linter!
