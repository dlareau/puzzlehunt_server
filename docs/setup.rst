Setup
*********

Instructions on how to setup a machine to run this project.

Server setup
------------

Install the following packages: 

- python 2.7
- mysql-client
- mysql-server
- python-mysqldb
- redis-server
- python-dev
- imagemagick
- libmysqlclient-dev

Install the following python packages using pip:

- django
- django-websocket-redis
- MySQL-python
- python-dateutil
- django-redis-sessions

Database setup
--------------

- expects a pre-existing empty database named puzzlehunt_db
- Database settings are in puzzlehunt_server/secret_settings.py the example used below has the following settings:
 a user named ```hunt``` on domain ```localhost``` with password ```wrongbaa``` with access to ```puzzlehunt_db```. Production values should be different. 
- The above can be accomplished by running the following commands as a superuser:
   - ```CREATE DATABASE puzzlehunt_db;```
   - ```CREATE USER 'hunt'@'localhost' IDENTIFIED BY 'wrongbaa';```
   - ```GRANT ALL PRIVILEGES ON puzzlehunt_db.* TO 'hunt'@'localhost' WITH GRANT OPTION;```
- run ```python manage.py migrate``` to have django configure the database
- then run ```python manage.py runserver 8080``` to start a server at http://127.0.0.1:8080/ (this will be replaced with nginx in the production version)