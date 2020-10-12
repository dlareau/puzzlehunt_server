
"""
Base Django settings for puzzlehunt_server project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import dirname, abspath
import codecs
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

BASE_DIR = dirname(dirname(dirname(abspath(__file__))))

# Application definition
SITE_TITLE = "Rice Puzzlehunt"

INSTALLED_APPS = (
    'bootstrap_admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'huntserver',
    'crispy_forms',
    'huey.contrib.djhuey',
)

SITE_ID = 1  # For flatpages

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'puzzlehunt_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'puzzlehunt_server/templates')],
        'OPTIONS': {
            'builtins': ['huntserver.templatetags.hunt_tags',
                         'huntserver.templatetags.prepuzzle_tags'],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "puzzlehunt"
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

HUEY = {
    'connection': {
        'host': 'redis',
    },
    'consumer': {
        'workers': 2,
    },
}


WSGI_APPLICATION = 'puzzlehunt_server.wsgi.application'

# URL settings
LOGIN_REDIRECT_URL = '/'
PROTECTED_URL = '/protected/'
LOGIN_URL = 'huntserver:login_selection'

# Random settings
SILENCED_SYSTEM_CHECKS = ["urls.W005"]  # silences admin url override warning
CRISPY_TEMPLATE_PACK = 'bootstrap3'
DEBUG_TOOLBAR_PATCH_SETTINGS = False
BOOTSTRAP_ADMIN_SIDEBAR_MENU = True
DEFAULT_HINT_LOCKOUT = 60  # 60 Minutes
HUNT_REGISTRATION_LOCKOUT = 2  # 2 Days

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static/Media files settings
STATIC_ROOT = "/static/"
STATIC_URL = '/static/'

MEDIA_ROOT = "/media/"
MEDIA_URL = '/media/'

# Shibboleth settings
USE_SHIBBOLETH = os.getenv("DJANGO_USE_SHIBBOLETH", default="False").lower() == "true"
SHIB_DOMAIN = os.getenv("DOMAIN", default="")

SHIB_ATTRIBUTE_MAP = {
    "Shib-Identity-Provider": (True, "idp"),
    "eppn": (True, "eppn"),
    "givenName": (False, "givenName"),
    "sn": (False, "sn")
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/external/django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'huntserver': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
}

# Email settings
CONTACT_EMAIL = 'mmr7@rice.edu'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587

# Environment variable overrides
if os.environ.get("ENABLE_DEBUG_EMAIL"):
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = '/tmp/test_folder'

if os.environ.get("ENABLE_DEBUG_TOOLBAR"):
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    MIDDLEWARE = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE

if os.environ.get("SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[DjangoIntegration()],

        # Sends which user caused the error
        send_default_pii=True
    )
