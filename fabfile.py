#!/usr/local/bin/python

import sys
import six
import functools
from fabric import Connection, task, Config
from fabric.main import Fab
from invoke.config import merge_dicts, DataProxy
from invoke import Argument, Collection

REPO_URL = 'https://github.com/dlareau/puzzlehunt_server.git'

LOCAL_DEFAULTS = {
    'user': 'hunt',
    'host': 'localhost',
    'install_folder': '../',
    'project_name': 'puzzlehunt_server',
    'connect_kwargs': None
}


# ===== Program setup =====
class TesterConfig(Config):
    prefix = "fabric"

    @staticmethod
    def global_defaults():
        their_defaults = Config.global_defaults()
        my_defaults = {
            'run': {
                'echo': True,
            },
        }
        return merge_dicts(their_defaults, my_defaults)


class PuzzlehuntManager(Fab):
    def core_args(self):
        core_args = super(PuzzlehuntManager, self).core_args()
        extra_args = [
            Argument(names=('remote',), help="Use remote host from settings file")
        ]
        return core_args + extra_args

    def update_config(self):
        super(Fab, self).update_config(merge=False)
        public_data = self.config._load_yaml("hosts_public.yaml")
        private_data = self.config._load_yaml("hosts_private.yaml")
        merge_dicts(public_data, private_data)

        remote = self.args["remote"].value
        if remote:
            public_data['remote'] = remote
        self.config.load_overrides(public_data)
        print(self.config)


# ===== Connection wrappers/helpers =====
def get_connection(ctx):
    try:
        with Connection(ctx.host.host, ctx.host.user, connect_kwargs=ctx.host.connect_kwargs) as conn:
            return conn
    except:
        return None


def connect(func):
    @functools.wraps(func)
    def wrapper(ctx, host=None, vname=None, **kwargs):
        if host is None or host == "local" or isinstance(ctx, Connection):
            # If the destination is local or not specified, populate local
            # config but do not make any connection
            local_defaults = DataProxy.from_data(LOCAL_DEFAULTS)
            if("local" in ctx.config.hosts):
                ctx.host = merge_dicts(local_defaults, ctx.config.hosts["local"])
            else:
                ctx.host = local_defaults
            conn = ctx
        else:
            # If the destination is remote and this isn't a connection object
            # populate the config and make the connection
            if host in ctx.config.hosts:
                ctx.host = ctx.config.hosts[host]
                conn = get_connection(ctx)
            else:
                print("Specified host not found in config file.")
                sys.exit(0)
        func(conn, **kwargs)
    return wrapper


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
    with ctx.cd(ctx.host.install_folder + ctx.host.project_name):
        if(full):
            ctx.sudo("service apache2 restart")
        else:
            ctx.run("touch puzzlehunt_server/wsgi.py")


@task
@connect
def install(ctx):
    pass


@task
def release(ctx, version=None):
    if("version" not in ctx.config):
        print("No version argument given. Exiting.")
        sys.exit(0)

    # Checks:
    with ctx.cd(ctx.host.install_folder + ctx.host.project_name):
        test(ctx)

        # Make sure all changes are committed
        git_status = ctx.run("git diff-index --quiet HEAD --", warn=True)
        if(git_status.failed):
            result = six.moves.input("You have uncommitted changes, do you want to continue? (y/n)")
            if(result.lower() != "y"):
                print("Aborting.")
                sys.exit(0)


    #ctx.run("cp foo bar")
    pass


@task
def deploy(ctx):
    ctx.run("ls")
    pass


@task
@connect
def prod_to_dev(ctx):
    pass


if __name__ == '__main__':
    local_collection = Collection.from_module(sys.modules[__name__])
    program = PuzzlehuntManager(config_class=TesterConfig,
                                namespace=local_collection,
                                version='1.0.0')
    program.run()
"""
2 scenarios:

task(connect(func)):
    - Fails because connect doesn't have the right arguments
    - Needs:
        - The task to know about the correct arguments:
    - Solution:
        - Make the task know about the arguments somehow
            - Maybe a third wrapper that modifies the returned task?


connect(task(func)):
    - Fails because the task isn't registered properly
        - Because it isn't a task
        - Wrapping it as a task again would mean the whole wrong arguments thing

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
