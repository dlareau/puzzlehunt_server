#!/bin/bash

# A setup file for rapid setup of a development environment in
# conjunction with vagrant. Debian specific.

# Variables
MYSQL_ROOT_PASSWORD=wrongbaa
MYSQL_NORMAL_USER=hunt
MYSQL_NORMAL_PASSWORD=puzzlehunt
MYSQL_PUZZLEHUNT_DB=puzzlehunt_db

# Make sure we don't get prompted for anything
export DEBIAN_FRONTEND="noninteractive"
debconf-set-selections <<< "mysql-server mysql-server/root_password password $MYSQL_ROOT_PASSWORD"
debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $MYSQL_ROOT_PASSWORD"

# Get all basic system packages
apt-get update
apt-get install -y git
apt-get install -y mysql-client
apt-get install -y mysql-server
apt-get install -y libmysqlclient-dev
apt-get install -y python-dev
apt-get install -y python-mysqldb
apt-get install -y python-pip

# Get the git repository and link it for external access
cd /vagrant
rm -rf puzzlehunt_server
git clone https://github.com/dlareau/puzzlehunt_server.git
ln -s /vagrant/puzzlehunt_server /home/vagrant/puzzlehunt_server
cd /home/vagrant/puzzlehunt_server

# Get all python dependencies and setup virtual environment
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up MYSQL user and database
mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE $MYSQL_PUZZLEHUNT_DB"
mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "grant all privileges on $MYSQL_PUZZLEHUNT_DB.* to '$MYSQL_NORMAL_USER'@'localhost' identified by '$MYSQL_NORMAL_PASSWORD'"

# Configure application (Consider this the same as modifying secret_settings.py.template)
cat > puzzlehunt_server/secret_settings.py <<EOF
SECRET_KEY = 'this is not the secret key, use your own'
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

# Run application setup commands
python manage.py migrate
python manage.py collectstatic --noinput
git checkout development # Only needed until test branch is merged
python manage.py loaddata config/initial_hunt.json

# We are root until this point, pass off ownership of all we have created
chown -R vagrant .

# Apache hosting setup
apt-get install -y apache2
apt-get install -y libapache2-mod-xsendfile
apt-get install -y libapache2-mod-proxy-html
apt-get install -y libapache2-mod-wsgi
a2enmod proxy
a2enmod proxy_http
a2enmod proxy_html
a2enmod xsendfile
a2enmod wsgi
cp config/puzzlehunt_vagrant.conf /etc/apache2/sites-enabled/
service apache2 restart