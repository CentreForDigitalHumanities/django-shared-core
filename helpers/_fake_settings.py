DEBUG = True
INSTALLED_APPS = [
     'django.contrib.contenttypes',
     'django.contrib.auth',
     'cdh.core',
     'cdh.rest',
     'cdh.vue',
     'cdh.files',
]
SECRET_KEY = "broodje_kaas"
LANGUAGE_CODE = 'nl'
LANGUAGES = (
    ('nl', 'lang:nl'),
    ('en', 'lang:en'),
)
