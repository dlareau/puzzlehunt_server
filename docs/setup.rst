Setup
*****

Instructions on how to setup a machine to run this project. 

Development Instructions
========================

If your only goal is to set up a working development or test environment, or if security really
isn't a concern for some reason, this project does come with an easy development deployment option.

1. Install Virtualbox. (https://www.virtualbox.org/wiki/Downloads)
2. Install Vagrant. (https://www.vagrantup.com/downloads.html)
3. Make a folder for the VM.
4. Clone this repository into that folder. (such that the folder you made now contains only one folder named "puzzlehunt_server")
5. Copy the Vagrantfile from the config folder within the puzzlehunt_server folder out into the folder that you made.
6. Run "vagrant up" from the folder you made and wait for it to complete.
7. You should now have the server running on a newly created VM, accessible via http://localhost:8080. The repository you cloned has been linked into the VM by vagrant, so any changes made to the repository on the host system should show up automatically. (A "vagrant reload" may be needed for some changes to take effect)

Production Instructions
=======================

Setting up the application on a production server should be done with a bit more care than the
vagrant script provides. The instructions below detail how to get mostly set up from a bare environment.

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
- unzip

Install the required python packages using:
``pip install -r requirements.txt``


Code Setup
----------

If you haven't already,
clone the repository to a location that the user running the server will have access to. 

Instantiate a copy of the local settings file by copying the local settings template::

	cp puzzlehunt_server/settings/local_settings.py.template puzzlehunt_server/settings/local_settings.py

Then replace the default settings such as the database login details  and secret key.
(If needed, look up instructions on how to generate a new secret key)

Database setup
--------------

This project is configured to use a MySQL database.
It can be configured to use a different type of database by modifying settings in local_settings.py,
but those modifications are out of the scope of this setup.

First we have to create the user and database that the application will use.
To do so, log into the mysql client as a superuser and enter the following commands.
(substituting your password and username)

::

	CREATE DATABASE puzzlehunt_db;

	GRANT ALL PRIVILEGES ON puzzlehunt_db.* TO 'nottherealusername'@'localhost' IDENTIFIED BY 'nottherealpassword';

Django setup
------------

Migrate the database by running ``python manage.py migrate``. 

Create a superuser for the project by running ``python manage.py createsuperuser`` and following the instructions.

Collect all of the static files by running ``python manage.py collectstatic``.

At this point the server should be able to start up.

Note: There are a few other steps before the server will function without error. For example the server expects at least one hunt object to exist. If you want some basic data to get started, you can run ``python manage.py loaddata initial_hunt``.

Apache setup
------------

The full setup of an apache server is beyond this documentation, but an example configuration file that should be a good starting point is available in the /config directory of the repository. That particular configuration file requires:  

- libapache2-mod-xsendfile
- libapache2-mod-proxy-html
- libapache2-mod-wsgi
- libapache2-mod-shib2

Part of the server and the apache configuration is the integration with Shibboleth for secure authentication of users. Again, this documentation couldn't possibly go over all aspects of setup. If you are setting this up from scratch, I recommend the following link:

`CMU Shibboleth Setup Instructions`_

.. _`CMU Shibboleth Setup Instructions`: http://www.cmu.edu/computing/services/security/identity-access/authentication/how-to/provider-shib.html

However replace the CMU provided shibboleth2.xml with the shibboleth2.xml in the /config directory of the repository.