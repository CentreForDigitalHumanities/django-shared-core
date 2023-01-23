from django.core.checks import Error, register, Tags
from django.conf import settings


@register(Tags.models)
def is_rest_app_loaded(app_configs, **kwargs):
    errors = []
    # If app_configs is None, Django instructs all apps to check themselves
    if app_configs is None or 'cdh.integration_platform' in app_configs:
        if 'cdh.rest' not in settings.INSTALLED_APPS:  # noQA
            errors.append(
                Error(
                    'cdh.rest is not added to INSTALLED_APPS. This app '
                    'depends on that app',
                    hint='Please add cdh.rest to your apps list (before this '
                         'app) in your settings file',
                    id='cdh.integration_platform.E001',
                )
            )

    return errors
