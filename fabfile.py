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
    'connect_kwargs': None,
    'server_secret_key': 'foobar',
    'mysql_db_name': 'test 1',
    'mysql_user_name': 'test 1',
    'mysql_user_password': 'test 2',
    'mysql_root_password': 'test 3',
    'mail_user_name': 'test 4',
    'mail_user_password': 'test 5',
    'allowed_hosts_string': '["*"]',
    'server_internal_ips': 'test 7',
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
    with ctx.cd(ctx.config.host.install_folder + ctx.config.host.project_name):
        if(full):
            ctx.sudo("service apache2 restart")
        else:
            ctx.run("touch puzzlehunt_server/wsgi.py")


@task
def install(ctx):
    # Need git to kick off the process
    ctx.sudo('apt-get update')
    ctx.sudo('apt-get install -y git')

    # Install mariadb (mysql) and related
    ctx.sudo('apt-get install -y mariadb-client mariadb-server libmariadbclient-dev')

    # Configure mariadb (mysql). Same as running mysql_secure_installation
    mysql_base = "mysql -uroot -p{} -e ".format(ctx.config.host.mysql_root_password)

    ctx.sudo(mysql_base + "\"UPDATE mysql.user SET Password=PASSWORD('{}') WHERE User='root'\"".format(ctx.config.host.mysql_root_password))
    ctx.sudo(mysql_base + "\"UPDATE mysql.user SET plugin='mysql_native_password' WHERE User='root'\"")
    ctx.sudo(mysql_base + "\"DELETE FROM mysql.user WHERE User=''\"")
    ctx.sudo(mysql_base + "\"DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1')\"")
    ctx.sudo(mysql_base + "\"DROP DATABASE IF EXISTS test\"")
    ctx.sudo(mysql_base + "\"DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%'\"")
    ctx.sudo(mysql_base + "\"FLUSH PRIVILEGES\"")
    ctx.sudo("service mariadb restart")

    # Install python related
    ctx.sudo('apt-get install -y python-dev python-mysqldb python-pip')

    # Install apache and related
    ctx.sudo('apt-get install -y apache2 libapache2-mod-xsendfile libapache2-mod-wsgi')
    # Apache hosting setup
    ctx.sudo('a2enmod proxy')
    ctx.sudo('a2enmod proxy_http')
    ctx.sudo('a2enmod proxy_html')
    ctx.sudo('a2enmod xsendfile')
    ctx.sudo('a2enmod wsgi')
    ctx.sudo("rm /etc/apache2/sites-enabled/*")

    # Install random other requirements
    ctx.sudo('apt-get install -y imagemagick unzip')

    # Sometimes this fails (which is apparently fine), so we do it separately
    ctx.sudo('apt-get install -y libapache2-mod-proxy-html', warn=True)

    # Set up MYSQL user and database
    mysql_login = "mysql -uroot -p{} -e".format(ctx.config.host.mysql_root_password)

    ctx.run('{} "CREATE DATABASE IF NOT EXISTS {}"'.format(mysql_login, ctx.config.host.mysql_db_name))
    ctx.run('{} "grant all privileges on {}.* to \'{}\'@\'localhost\' identified by \'{}\'"'.format(
        mysql_login, ctx.config.host.mysql_db_name, ctx.config.host.mysql_user_name, ctx.config.host.mysql_user_password))
    ctx.run('{} "grant all privileges on test_{}.* to \'{}\'@\'localhost\'"'.format(
        mysql_login, ctx.config.host.mysql_db_name, ctx.config.host.mysql_user_name))

    # Make local_settings
    file_contents = ""
    file_contents += "from .base_settings import *\n"
    file_contents += "DEBUG = False\n"
    file_contents += "SECRET_KEY = {}\n".format(ctx.config.host.server_secret_key)
    file_contents += "DATABASES = {\n"
    file_contents += "    'default': {\n"
    file_contents += "        'ENGINE': 'django.db.backends.mysql',\n"
    file_contents += "        'NAME': '{}',\n".format(ctx.config.host.mysql_db_name)
    file_contents += "        'HOST': 'localhost',\n"
    file_contents += "        'PORT': '3306',\n"
    file_contents += "        'USER': '{}',\n".format(ctx.config.host.mysql_user_name)
    file_contents += "        'PASSWORD': '{}',\n".format(ctx.config.host.mysql_user_password)
    file_contents += "        'OPTIONS': {'charset': 'utf8mb4'},\n"
    file_contents += "    }\n"
    file_contents += "}\n"
    file_contents += "INTERNAL_IPS = '{}'\n".format(ctx.config.host.server_internal_ips)
    file_contents += "EMAIL_HOST_USER = '{}'\n".format(ctx.config.host.mail_user_name)
    file_contents += "EMAIL_HOST_PASSWORD = '{}'\n".format(ctx.config.host.mail_user_password)
    file_contents += "ALLOWED_HOSTS = {}\n".format(ctx.config.host.allowed_hosts_string)

    ctx.run("cat << EOS > new_file\n" + file_contents + "EOS", echo=False)


@task
def release(ctx, version=None):
    if(version is None):
        print("No version argument given. Exiting.")
        sys.exit(0)

    with ctx.cd(ctx.config.host.install_folder + ctx.config.host.project_name):
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
    with ctx.cd(ctx.config.host.install_folder):
        ctx.run("git clone {} {}".format(REPO_URL, ctx.config.host.project_name))
        with ctx.cd(ctx.config.host.project_name):
            ctx.run('git checkout {}'.format(ctx.config.host.branch))

    # Get all python dependencies and setup virtual environment
    ctx.run('pip install virtualenv')
    ctx.run('./venv/bin/pip install -r requirements.txt')

    # Run application setup commands
    with ctx.cd(ctx.config.host.install_folder):
        with ctx.cd(ctx.config.host.project_name):
            ctx.run('mkdir -p ./media/puzzles')
            ctx.run('mkdir -p ./media/prepuzzles')
            ctx.run('./venv/bin/python manage.py migrate')
            ctx.run('./venv/bin/python manage.py collectstatic --noinput')
            ctx.run('./venv/bin/python manage.py loaddata initial_hunt')

            ctx.run('chgrp -R www-data ./media')
            ctx.run('chmod -R go+r .')
            ctx.run('chmod -R og+rw ./media')

    # TODO: Update this
    # modify and copy configuration
    ctx.run('sed "s/vagrant/$USERNAME/g" config/puzzlehunt_generic.conf > /etc/apache2/sites-enabled/puzzlehunt_generic.conf')
    ctx.run('service apache2 restart')
    pass


@task
def backup_db(ctx):
    pass


@task
def status(ctx):
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
    - Check install for debian based host before proceeding

Deploy:
 - Run tests
 - pull specified version from server
 - Update dependencies
 - Update secret settings
 - migrate
 - copy static files
 - Update config files
 - restart server
 - Update apache files
 - Status checks on everything
 - tell Senctx.run('that we've deployed')
 - options:
    - restart nicely
    - force deployment (use tip and/or test check)
    - choose deployment environment
"""
