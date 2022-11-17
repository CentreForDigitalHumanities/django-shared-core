DEBUG = True
INSTALLED_APPS = [
     'django.contrib.contenttypes',
     'django.contrib.auth',
     'modeltranslation',
     'cdh.core',
     'cdh.rest',
     'cdh.vue',
     'cdh.files',
     'cdh.systemmessages',
]
SECRET_KEY = "broodje_kaas"
LANGUAGE_CODE = 'nl'
LANGUAGES = (
    ('nl', 'lang:nl'),
    ('en', 'lang:en'),
)
