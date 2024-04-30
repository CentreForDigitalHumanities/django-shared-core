from django.conf import settings

CDH_EMAIL_THEME_SETTINGS = {
    'outer_container_width': '1000px',
    'main_background': "#eee",
    'banner_background': "#000",
    'banner_color': "#fff",
    'content_background': "#fff",
    'content_color': "#333",
    'footer_background': "#333",
    'footer_color': "#fff",
    'footer_stripe': True,
    'footer_stripe_color': "#C00A35",
}

_theme_app_conf = getattr(
    settings,
    'CDH_EMAIL_THEME_SETTINGS',
    {},
)

CDH_EMAIL_THEME_SETTINGS.update(_theme_app_conf)

CDH_EMAIL_PLAIN_FALLBACK_TEMPLATE = getattr(
    settings,
    'CDH_EMAIL_PLAIN_FALLBACK_TEMPLATE',
    "cdh.mail/plain_mail_fallback.txt",
)

CDH_EMAIL_HTML_FALLBACK_TEMPLATE = getattr(
    settings,
    "CDH_EMAIL_HTML_FALLBACK_TEMPLATE",
    "cdh.mail/mail_template.html",
)

CDH_EMAIL_FAIL_SILENTLY = getattr(
    settings,
    'CDH_EMAIL_FAIL_SILENTLY',
    True,
)
