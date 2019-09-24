
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
    'django_nose',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--cover-package=huntserver',
    '--cover-erase',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
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


# Database information now in file not tracked by git

# Login redirect override from /accounts/profile/ to /

LOGIN_REDIRECT_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_TITLE = "Puzzlehunt CMU"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
MEDIA_URL = '/media/'

DEBUG_TOOLBAR_PATCH_SETTINGS = False

BOOTSTRAP_ADMIN_SIDEBAR_MENU = True

PROTECTED_URL = '/protected/'
LOGIN_URL = '/login-selection/'


# Shibboleth options
USE_SHIBBOLETH = True

SHIB_ATTRIBUTE_MAP = {
    "Shib-Identity-Provider": (True, "idp"),
    "eppn": (True, "eppn"),
    "givenName": (False, "givenName"),
    "sn": (False, "sn")
}

SHIB_USERNAME = "eppn"
SHIB_EMAIL = "eppn"
SHIB_FIRST_NAME = "givenName"
SHIB_LAST_NAME = "sn"

# Logging options
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

# Email options
CONTACT_EMAIL = 'puzzlehunt-staff@lists.andrew.cmu.edu'

#Comment out for production.
#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '/tmp/test_folder'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587

