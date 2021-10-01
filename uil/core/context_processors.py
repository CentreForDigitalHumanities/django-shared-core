from django.conf import settings


def acceptation(request):
    """
    Returns if the app is set to acceptation mode
    """
    context_extras = {}
    if hasattr(settings, 'ACCEPTATION'):
        context_extras['acceptation'] = settings.ACCEPTATION
    else:
        context_extras['acceptation'] = False

    return context_extras