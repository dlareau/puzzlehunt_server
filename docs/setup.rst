Setup
*********

Instructions on how to setup a machine to run this project.

Environment setup
-----------------

Install the following packages: 

- python 2.7
- mysql-client
- mysql-server
- python-mysqldb
- python-dev
- imagemagick
- libmysqlclient-dev

Install the required python packages using:
``pip install -r requirements.txt``


Code Setup
----------

If you haven't already,
clone the repository to a location that the user running the server will have access to. 

Instantiate a copy of the secret settings file by copying the secret settings template::

	cp puzzlehunt_server/secret_settings.py.template puzzlehunt_server/secret_settings.py

Then replace the default settings such as the database login details  and secret key.
(If needed, look up instructions on how to generate a new secret key)

Database setup
--------------

This project is configured to use a MySQL database.
It can be configured to use a different type of database by modifying settings in secret_settings.py,
but those modifications are out of the scope of this setup.

First we have to create the user and database that the application will use.
To do so, log into the mysql client as a superuser and enter the following commands.
(substituting your password and username)

::

	CREATE DATABASE puzzlehunt_db;

	CREATE USER 'nottherealusername'@'localhost' IDENTIFIED BY 'nottherealpassword';

	GRANT ALL PRIVILEGES ON puzzlehunt_db.* TO 'nottherealusername'@'localhost' WITH GRANT OPTION;

Django setup
------------

Migrate the database by running ``python manage.py migrate``. 

Create a superuser for the project by running ``python manage.py createsuperuser`` and following the instructions.

Collect all of the static files by running ``python manage.py collectstatic``.

At this point the server should be able to start up.
	Developers note: There may be a few other steps before the server will function without error. For example I believe it expects at least one hunt object to exist. I hope to one day have those needs either be documented or not exist any more.

Apache setup
------------

The full setup of an apache server is beyond this documentation, but an example configuration file that should be a good starting point is available in the /config directory of the repository.

Part of the server and the apache configuration is the integration with Shibboleth for secure authentication of users. Again, this documetation couldn't possibly go over all aspects of setup. If you are setting this up from scratch, I reccommend the following link:

`CMU Shibboleth Setup Instructions`_

.. _`CMU Shibboleth Setup Instructions`: http://www.cmu.edu/computing/services/security/identity-access/authentication/how-to/provider-shib.html

However replace the CMU provided shibboleth2.xml with the shibboleth2.xml in the /config directory of the repository.