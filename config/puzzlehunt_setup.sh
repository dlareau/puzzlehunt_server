#!/bin/bash

# A setup file for rapid setup of a development environment in
# conjunction with vagrant. Debian specific.

# Nothing about this setup is secure, this is absolutely not for production

# Variables
USERNAME=vagrant
MYSQL_ROOT_PASSWORD=wrongbaa
MYSQL_NORMAL_USER=hunt
MYSQL_NORMAL_PASSWORD=$(head /dev/urandom | LC_ALL=C tr -dc 'A-Za-z0-9!@#$%^&*(\-_=+)' | head -c 16)
MYSQL_PUZZLEHUNT_DB=puzzlehunt_db

# Helper functions
try() { "$@" || (echo "$0: cannot $*" >&2; exit 1;)}

getent passwd $USERNAME > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "$USERNAME user already exists"
else
	try adduser --gecos "" --disabled-password $USERNAME
fi

# Need git to kick off the process
try apt-get update
try apt-get install -y git

# Get the git repository and link it for external access
# Consider checking and cloning
try ln -s -f /vagrant/puzzlehunt_server /home/$USERNAME/puzzlehunt_server
try cd /home/$USERNAME/puzzlehunt_server
try git checkout development

# Make sure we don't get prompted for anything
try export DEBIAN_FRONTEND="noninteractive"
try debconf-set-selections <<< "mysql-server mysql-server/root_password password $MYSQL_ROOT_PASSWORD"
try debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $MYSQL_ROOT_PASSWORD"

# Get all basic system packages
try apt-get install -y mysql-client mysql-server libmysqlclient-dev python-dev python-mysqldb python-pip apache2 libapache2-mod-xsendfile libapache2-mod-wsgi imagemagick

# Sometimes this isn't needed
try apt-get install -y libapache2-mod-proxy-html || true

# Set up MYSQL user and database
try mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $MYSQL_PUZZLEHUNT_DB"
try mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "grant all privileges on $MYSQL_PUZZLEHUNT_DB.* to '$MYSQL_NORMAL_USER'@'localhost' identified by '$MYSQL_NORMAL_PASSWORD'"
try mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "grant all privileges on test_$MYSQL_PUZZLEHUNT_DB.* to '$MYSQL_NORMAL_USER'@'localhost'"

# Configure application (Consider this the same as making local_settings.py)
try cat > puzzlehunt_server/settings/local_settings.py <<EOF
from .base_settings import *
DEBUG=False
SECRET_KEY = '$(head /dev/urandom | LC_ALL=C tr -dc 'A-Za-z0-9!@#$%^&*(\-_=+)' | head -c 50)'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '$MYSQL_PUZZLEHUNT_DB',
        'HOST': 'localhost',
        'PORT': '3306',
        'USER': '$MYSQL_NORMAL_USER',
        'PASSWORD': '$MYSQL_NORMAL_PASSWORD',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
INTERNAL_IPS = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EOF


# Get all python dependencies and setup virtual environment
try pip install virtualenv
try virtualenv venv
try source venv/bin/activate
try pip install -r requirements.txt

# Run application setup commands
try mkdir -p ./media/puzzles
try export DJANGO_SETTINGS_MODULE=puzzlehunt_server.settings.local_settings
try python manage.py migrate
try python manage.py collectstatic --noinput
try python manage.py loaddata initial_hunt
try deactivate

# We are root until this point, pass off ownership of all we have created
try chown -R $USERNAME .
try chmod -R go+r .
try chmod -R og+rw ./media

# Apache hosting setup
try a2enmod proxy
try a2enmod proxy_http
try a2enmod proxy_html
try a2enmod xsendfile
try a2enmod wsgi
rm /etc/apache2/sites-enabled/*

# modify and copy configuration
try sed "s/vagrant/$USERNAME/g" config/puzzlehunt_generic.conf > /etc/apache2/sites-enabled/puzzlehunt_generic.conf
try service apache2 restart

echo $(ip address show eth0 | grep 'inet ' | sed -e 's/^.*inet //' -e 's/\/.*$//')