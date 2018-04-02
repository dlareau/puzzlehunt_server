#!/bin/bash

# Setup script. Debian (and variant) specific

# Variables
MYSQL_ROOT_PASSWORD=wrongbaa
MYSQL_NORMAL_USER=hunt
MYSQL_NORMAL_PASSWORD=$(head /dev/urandom | LC_ALL=C tr -dc 'A-Za-z0-9!@#$%^&*(\-_=+)' | head -c 16)
MYSQL_PUZZLEHUNT_DB=puzzlehunt_db

# Helper functions
yell() { echo "$0: $*" >&2; }
die() { yell "$*"; cd ~puzzlehunt; rm -rf puzzlehunt_server; exit 111; }
try() { "$@" || die "cannot $*"; }

# Create puzzlehunt user

getent passwd puzzlehunt > /dev/null 2&>1
if [ $? -eq 0 ]; then
    echo "Puzzlehunt User already exists"
else
	try adduser --gecos "" --disabled-password puzzlehunt
fi

# Need git to kick off the process
try apt-get update
try apt-get install -y git

# Get the git repository
try cd ~puzzlehunt
try git clone https://github.com/dlareau/puzzlehunt_server.git
try cd puzzlehunt_server

# Make sure we don't get prompted for anything 
try export DEBIAN_FRONTEND="noninteractive"
try debconf-set-selections <<< "mysql-server mysql-server/root_password password $MYSQL_ROOT_PASSWORD"
try debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $MYSQL_ROOT_PASSWORD"

# Get all basic system packages
try apt-get install -y mysql-client mysql-server libmysqlclient-dev python-dev python-mysqldb python-pip apache2 libapache2-mod-xsendfile libapache2-mod-wsgi

apt-get install -y libapache2-mod-proxy-html || true

# Set up MYSQL user and database
try mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $MYSQL_PUZZLEHUNT_DB"
try mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "grant all privileges on $MYSQL_PUZZLEHUNT_DB.* to '$MYSQL_NORMAL_USER'@'localhost' identified by '$MYSQL_NORMAL_PASSWORD'"

# Configure application (Consider this the same as modifying secret_settings.py.template)
try cat > puzzlehunt_server/secret_settings.py <<EOF
SECRET_KEY = '$(head /dev/urandom | LC_ALL=C tr -dc 'A-Za-z0-9!@#$%^&*(\-_=+)' | head -c 50)'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '$MYSQL_PUZZLEHUNT_DB',
        'HOST': 'localhost',
        'PORT': '3306',
        'USER': '$MYSQL_NORMAL_USER',
        'PASSWORD': '$MYSQL_NORMAL_PASSWORD',
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
try python manage.py migrate
try python manage.py collectstatic --noinput
try git checkout generic # Only needed until test branch is merged
try python manage.py loaddata initial_hunt.json
try deactivate

# We are root until this point, pass off ownership of all we have created
try chown -R puzzlehunt .

# Apache hosting setup
try a2enmod proxy
try a2enmod proxy_http
try a2enmod proxy_html
try a2enmod xsendfile
try a2enmod wsgi
try cp config/puzzlehunt.conf /etc/apache2/sites-enabled/
try service apache2 restart