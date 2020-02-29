
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
SITE_TITLE = "Puzzlehunt CMU"

INSTALLED_APPS = (
    'bootstrap_admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'huntserver',
    'crispy_forms',
)


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

WSGI_APPLICATION = 'puzzlehunt_server.wsgi.application'

# URL settings
LOGIN_REDIRECT_URL = '/'
PROTECTED_URL = '/protected/'
LOGIN_URL = 'login_selection'

# Random settings
CRISPY_TEMPLATE_PACK = 'bootstrap3'
DEBUG_TOOLBAR_PATCH_SETTINGS = False
BOOTSTRAP_ADMIN_SIDEBAR_MENU = True
DEFAULT_HINT_LOCKOUT = 60  # 60 Minutes
HUNT_REGISTRATION_LOCKOUT = 2  # 2 Days

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
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

# Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'noop': {
            'level': 'WARNING',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {},
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
}

# Email settings
CONTACT_EMAIL = 'puzzlehunt-staff@lists.andrew.cmu.edu'

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
