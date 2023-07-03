ENABLE_DEBUG_TOOLBAR = True

# Django settings extensions
DEV_TOOLS_APPS = [
    'cdh.dev_tools',
    'debug_toolbar',
]

DEV_TOOLS_MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Email
EMAIL_BACKEND = 'mail_panel.backend.MailToolbarBackend'
EMAIL_FROM = 'portaldev.gw@uu.nl'

# Panels config
DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
    "mail_panel.panels.MailToolbarPanel",
    "cdh.dev_tools.debug_toolbar.panels.RestClientPanel",
]