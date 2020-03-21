Setup
*****

Instructions on how to setup a machine to run this project.

Basic Setup Instructions
========================

This project now uses docker-compose as it's main form of setup. You can use the
following steps to get a sample server up and going

1. Install [docker/docker-compose.](https://docs.docker.com/compose/install/)
2. Clone this repository.
3. Make a copy of ``sample.env`` named ``.env`` (yes, it starts with a dot).
4. Edit the new ``.env`` file, filling in new values for the first block of
uncommented lines. Other lines can be safely ignored as they only provide
additional functionality.
5. Run ``docker-compose up`` (possibly prepending ``sudo`` if needed)
6. You should now have the server running on a newly created VM, accessible via
[http://localhost](http://localhost). The repository you cloned has been linked
into the VM by docker, so any changes made to the repository on the host system
should show up automatically. (A ``docker-compose restart`` may be needed for
some changes to take effect)

Setup details
-------------

The basic instructions above bring up the following docker containers:

- db: The postgres database with the settings specified in the .env file. Data
    is retained across container restarts in ``docker/volumes/redis_data``.
- redis: A redis server for caching and task management. Data is stored in
    ``docker/volumes/redis_data``.
- app: The Django application running using gunicorn on port 8000.
- huey: A Huey consumer for scheduled tasks.
- web: An apache server to proxy web requests to the "app" container and serve
    the static files. By default, this container serves web requests using plain
    HTTP over port 80. See the "Extra Setup Instructions" for details on
    setting up SSL.

.. Note::
   There are also 2 volumes shared by a number of the containers that hold
   static files and media files and will persist across docker restarts.

Extra Setup Instructions
=======================

In addition to the basic instructions above, there are a few additional setup
options available. These additional options are provided via "override files"
that override various parts of the docker compose logic. You can enable which
override files are being used by setting the ``COMPOSE_FILE`` variable in the
``.env`` file. By default only the ``local_override.yml`` file is enabled.

local_override
--------------

By default, the "web" docker container only "exposes" port 80. The local
override file takes things one step further and maps the host port 80 to the
web container port 80. This is done via an override because docker compose
doesn't support unmapping ports and the proxy_override settings need to map
the reverse proxy to host port 80.

shib_override
-------------

Enabling this override sets up shibboleth authentication on the apache server.
To use pre-existing shibboleth certificates, place sp-cert.pem and sp-key.pem
in ``docker/volumes/shib-certs``. This override file
also uses LetsEncrypt to get a certificate for the site using the DOMAIN
and CONTACT_EMAIL settings from the ``.env`` file. SSL certs are stored in
``docker/volumes/ssl-certs``. Right now this is the only override that provides
SSL capabilities. In the future there will likely be an SSL_override file that
breaks out the LetsEncrypt functionality.

proxy_override
--------------

Enabling this override file sets up a reverse proxy using Traefik. This
functionality is in development and mostly untested. It currently only works
with shib_override. It also requires an already created docker network named
``proxy-net``