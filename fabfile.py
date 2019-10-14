import sys
import functools
from fabric import Connection, task
from invoke import Responder
from fabric.config import Config

REPO_URL = 'https://github.com/dlareau/puzzlehunt_server.git'
INSTALL_FOLDER = "/home/hunt/"


# ===== Connection wrappers/helpers =====
def get_connection(ctx):
    try:
        with Connection(ctx.host, ctx.user, connect_kwargs=ctx.connect_kwargs) as conn:
            return conn
    except:
        return None


def connect(func):
    @functools.wraps(func)
    def wrapper(ctx):
        if isinstance(ctx, Connection):
            conn = ctx
        else:
            conn = get_connection(ctx)
        func(conn)
    return wrapper


# ===== Environments =====
@task
def development(ctx):
    ctx.user = "hunt"
    ctx.host = "puzzlehunt.club.cc.cmu.edu"
    ctx.project_name = "puzzlehunt_server"


# ===== Private helper functions =====
def clone(ctx):
    ls_result = ctx.run("ls").stdout
    ls_result = ls_result.split("\n")
    if ctx.project_name in ls_result:
        print("Project already exists")
        return
    return ctx.run("git clone {} {}".format(REPO_URL, ctx.project_name))


def migrate(ctx):
    return ctx.run("./venv/bin/python manage.py migrate")


def test(ctx):
    return ctx.run("./venv/bin/python manage.py test")


def install_dependencies(ctx):
    return ctx.run("./venv/bin/pip -r requirements.txt")


def collect_static_files(ctx, clear=False):
    if(clear):
        clear_flag = "--clear"
    else:
        clear_flag = ""
    return ctx.run("./venv/bin/python manage.py collectstatic --noinput " + clear_flag)


# ===== Public routines =====
@task
@connect
def restart(ctx, full=False):
    with ctx.cd(INSTALL_FOLDER + ctx.project_name):
        if(full):
            ctx.sudo("service apache2 restart")
        else:
            ctx.run("touch puzzlehunt_server/wsgi.py")


@task
@connect
def install(ctx):
    pass


@task
def release(ctx):
    # Checks:
    test(ctx)

    pass


@task
@connect
def deploy(ctx):
    pass


@task
@connect
def prod_to_dev(ctx):
    pass


@task
@connect
def deploy(ctx):
    pass
"""
Still need:
    - Backup DB
    - Update config files
    - Status

Other Thoughts:
Create:
 - Create user
 - Install git
 - Install packages
 - Enable apache mods
 - Create database

Release:
 - Run tests
 - Create git tag
 - Create sentry version
 - Associate commits with sentry version
 - Updates version in files


Deploy:
 - Run tests
 - pull specified version from server
 - Update dependencies
 - Update secret settings
 - migrate
 - copy static files
 - restart server
 - Update apache files
 - Status checks on everything
 - tell Sentry that we've deployed
 - options:
    - restart nicely
    - force deployment (use tip and/or test check)
    - choose deployment environment


List of environment non-secrets
 - Version #
 - Environment name
 - sql_db_name
 - sql_db_username
 - allowed_hosts?
 - email_user
 - logging details
 - apache config

List of environment secrets
 - sql_db_password
 - internal_ips
 - email_password
 - secret key

"""
