from .base_settings import *
import os

DEBUG = os.environ.get("DJANGO_ENABLE_DEBUG") == "True"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("DJANGO_DB_NAME"),
        'HOST': 'db',
        'PORT': '',
        'USER': os.environ.get("DJANGO_DB_USER"),
        'PASSWORD': os.environ.get("DJANGO_DB_PASSWORD"),
        #'OPTIONS': {'charset': 'utf8mb4'},
    }
}
INTERNAL_IPS = ['127.0.0.1', 'localhost',]
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_PASSWORD")

ALLOWED_HOSTS = ['*']