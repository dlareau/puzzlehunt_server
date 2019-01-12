from .base_settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SECRET_KEY = '$1B&VUf$OdUEfMJXd40qdakA36@%2NE_41Dz9tFs6l=z4v_3P-'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'puzzlehunt_db',
        'HOST': '127.0.0.1',
        'USER': 'root',
        'PASSWORD': '',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
INTERNAL_IPS = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''