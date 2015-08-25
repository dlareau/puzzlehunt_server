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

Code Setup
----------

If you haven't already,
clone the repository to a location that the user running the server will have access to. 

Instantiate a copy of the secret settings file by copying the secret settings template:
    ``cp puzzlehunt_server/secret_settings.py.template puzzlehunt_server/secret_settings.py``

Then replace the default settings such as the admin account username,
the database login details, and secret key.
(If needed, look up instructions on how to generate a new secret key)

Database setup
--------------

This project is configured to use a MySQL database.
It can be configured to use a different type of database by modifying settings in secret_settings.py,
but those modifications are out of the scope of this setup.

First we have to create the user and database that the application will use.
To do so, log into the mysql client as a superuser and enter the following commands.
(subsituting your password and username)

- ``CREATE DATABASE puzzlehunt_db;``
- ``CREATE USER 'nottherealusername'@'localhost' IDENTIFIED BY 'nottherealpassword';``
- ``GRANT ALL PRIVILEGES ON puzzlehunt_db.* TO 'nottherealusername'@'localhost' WITH GRANT OPTION;``


Redis setup
-----------

Start up the redis server using ``sudo service redis-server start``.
You can check if worked by running ``redis-cli ping`` and getting the response ``PONG``.

Django setup
------------

Migrate the database by running ``python manage.py migrate``. 

Create a superuser for the project by running ``python manage.py createsuperuser`` and following the instructions.
The username here should be one of the usernames in the setting ADMIN_ACCTS in secret_settings.py.

Run ```python manage.py runserver 8080``` to start a server at http://127.0.0.1:8080/

Nginx setup
-----------

Coming soon! (Use the test server command above until then)
