from .base_settings import *
import dj_database_url
import os

DEBUG = os.getenv("DJANGO_ENABLE_DEBUG", default="False").lower() == "true"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DATABASES = {'default': dj_database_url.config(conn_max_age=600)}

if(DATABASES['default']['ENGINE'] == 'django.db.backends.mysql'):
    DATABASES['default']['OPTIONS'] = {'charset': 'utf8mb4'}

INTERNAL_IPS = ['127.0.0.1', 'localhost']
EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST")
EMAIL_PORT = os.environ.get("DJANGO_EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_PASSWORD")
EMAIL_FROM = os.environ.get("DJANGO_EMAIL_FROM")
DOMAIN = os.getenv("DOMAIN", default="default.com")
CHAT_ENABLED = os.getenv("PUZZLEHUNT_CHAT_ENABLED", default="True").lower() == "true"

ALLOWED_HOSTS = ['*']
