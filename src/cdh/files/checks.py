from django.core.checks import Warning, Error, register, Tags
import cdh.files.settings as settings


@register(Tags.models)
def example_check(app_configs, **kwargs):
    errors = []
    # If app_configs is None, Django instructs all apps to check themself
    if app_configs is None or 'cdh.files' in app_configs:
        if not settings._tlum_loaded and settings.TRACK_CREATED_BY:  # noQA
            errors.append(
                Error(
                    'ThreadLocalUserMiddleware is not loaded as middleware. '
                    'but CDH_FILES_TRACK_CREATED_BY is enabled manually.',
                    hint='Please add '
                         'cdh.core.middleware.ThreadLocalUserMiddleware to '
                         'your middleware list (after the authentication '
                         'middleware) in your settings file',
                    id='cdh.files.E001',
                )
            )
        elif not settings._tlum_loaded:
            errors.append(
                Warning(
                    'ThreadLocalUserMiddleware is not loaded as middleware. '
                    'cdh.files will not be able to keep track of who created '
                    'which files.',
                    hint='This is not necessary, and can be safely silenced. '
                         'If it is desired, insert '
                         'cdh.core.middleware.ThreadLocalUserMiddleware into '
                         'your middleware list (after the authentication '
                         'middleware) in your settings file',
                    id='cdh.files.W001',
                )
            )

    return errors
