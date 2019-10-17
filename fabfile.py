#!/usr/local/bin/python
import sys
import six
from fabric import task, Config, Executor, Connection
from fabric.main import Fab
from fabric.tasks import ConnectionCall
from invoke.config import merge_dicts, DataProxy
from invoke import Collection

REPO_URL = 'https://github.com/dlareau/puzzlehunt_server.git'

LOCAL_DEFAULTS = {
    'user': 'hunt',
    'host': 'localhost',
    'install_folder': '../',
    'project_name': 'puzzlehunt_server',
    'connect_kwargs': None
}


# ===== Program setup (Overriding Fabric to use host files) =====
class PuzzlehuntManager(Fab):
    # Adds in my opinions (run:echo=True) and the settings from the hosts files
    def update_config(self):
        super(PuzzlehuntManager, self).update_config()
        public_data = self.config._load_yaml("hosts_public.yaml")
        private_data = self.config._load_yaml("hosts_private.yaml")
        hosts = dict(hosts=merge_dicts(public_data, private_data))
        self.config.load_overrides(hosts)

        defaults = Config.global_defaults()
        local_default = DataProxy.from_data(LOCAL_DEFAULTS)
        if("local" in public_data):
            merge_dicts(local_default, public_data["local"])
        my_defaults = {
            'run': {'echo': True},
            'host': local_default
        }
        merge_dicts(defaults, my_defaults)
        self.config.load_defaults(defaults)


class ConfigConnectionCall(ConnectionCall):
    # Same as parent but doesn't stomp on config values
    def make_context(self, config):
        kwargs = self.init_kwargs
        kwargs["config"] = merge_dicts(config, kwargs["config"])
        return Connection(**kwargs)


class FileConfigExecutor(Executor):
    # Normalizes hosts using settings from host files
    def normalize_hosts(self, hosts):
        new_hosts = []
        file_hosts = self.config.hosts
        for value in hosts or []:
            if isinstance(value, dict):
                short_host = value['host']
            else:
                short_host = value
            if(short_host not in file_hosts):
                print("Given host does not have any configuration information.")
                sys.exit(0)
            if not isinstance(value, dict):
                value = dict()
            value['host'] = file_hosts[short_host]['host']
            value['user'] = file_hosts[short_host].get('user', None)
            file_kwargs = file_hosts[short_host].get('connect_kwargs', {})
            existing_kwargs = value.get('connect_kwargs', {})
            value['connect_kwargs'] = merge_dicts(existing_kwargs, file_kwargs)
            value['config'] = dict(host=file_hosts[short_host])
            new_hosts.append(value)
        return new_hosts

    # Same as parent but uses ConfigConnectionCall
    def parameterize(self, call, connection_init_kwargs):
        new_call_kwargs = dict(init_kwargs=connection_init_kwargs)
        return call.clone(into=ConfigConnectionCall, with_=new_call_kwargs)


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
    return ctx.run("./venv/bin/python manage.py test --noinput")


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
def restart(ctx, full=False):
    with ctx.cd(ctx.host.install_folder + ctx.host.project_name):
        if(full):
            ctx.sudo("service apache2 restart")
        else:
            ctx.run("touch puzzlehunt_server/wsgi.py")


@task
def install(ctx):
    pass


@task
def release(ctx, version=None):
    if(version is None):
        print("No version argument given. Exiting.")
        sys.exit(0)

    with ctx.cd(ctx.host.install_folder + ctx.host.project_name):
        # Run django test suite
        test(ctx)

        # Make sure all changes are committed
        git_status = ctx.run("git diff-index --quiet HEAD --", warn=True)
        if(git_status.failed):
            result = six.moves.input("You have uncommitted changes, do you want to continue? (y/n): ")
            if(result.lower() != "y"):
                print("Aborting.")
                sys.exit(0)

        # Make sure we have some release notes
        git_status = ctx.run("grep v{} docs/changelog.rst".format(version), warn=True)
        if(git_status.failed):
            result = six.moves.input("There is nothing in the changelog for this version, do you want to continue? (y/n): ")
            if(result.lower() != "y"):
                print("Aborting.")
                sys.exit(0)

        # Create the release tag
        ctx.run('git tag -a -f v{} -m "v{}"'.format(version, version))

        # Check for sentry and do the sentry stuff here

        ctx.run("git push origin v{}".format(version))

    pass


@task
def deploy(ctx):
    ctx.run("ls")
    pass


@task
def prod_to_dev(ctx):
    pass


if __name__ == '__main__':
    local_collection = Collection.from_module(sys.modules[__name__])
    program = PuzzlehuntManager(config_class=Config,
                                namespace=local_collection,
                                executor_class=FileConfigExecutor,
                                version='1.0.0')
    program.run()
"""
TODO:
    - Include sentry and fabric in requirements.txt
    - Put sentry stuff in release task
    - Figure out how to put apache config in

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
"""
