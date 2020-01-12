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
    'apache_file': 'puzzlehunt_generic.conf'
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
                sys.exit(1)
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
def test(ctx):
    return ctx.run("./venv/bin/python3 manage.py test --noinput")

# ===== Public routines =====
@task
def restart(ctx, full=False):
    with ctx.cd(ctx.config.host.install_folder + ctx.config.host.project_name):
        if(full):
            ctx.sudo("service apache2 restart")
        else:
            ctx.run("touch puzzlehunt_server/wsgi.py")


@task
def deploy(ctx, initial=False, ssl=False):
    install_folder = ctx.config.host.install_folder
    project_name = ctx.config.host.project_name
    project_folder = install_folder + project_name
    hostname = ctx.config.host.host
    apache_file = ctx.config.host.apache_file
    # Safe to assume gmail for now because smtp.gmail.com is hardcoded into base_settings.py
    contact_email = ctx.config.host.mail_user_name + "@gmail.com"

    directory_check = ctx.run('[ -d {} ]'.format(project_folder), warn=True)
    if(directory_check.failed):
        ctx.sudo("mkdir -p {}".format(install_folder))
        ctx.sudo("chown $USER: {}".format(install_folder))
        with ctx.cd(ctx.config.host.install_folder):
            ctx.run("git clone {} {}".format(REPO_URL, project_name))

    # Make local_settings
    file_contents = ""
    file_contents += "from .base_settings import *\n"
    file_contents += "DEBUG = False\n"
    file_contents += "SECRET_KEY = '{}'\n".format(ctx.config.host.server_secret_key)
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

    # Run application setup commands
    with ctx.cd(project_folder):
        ctx.run("git pull")
        with ctx.cd("puzzlehunt_server/settings"):
            ctx.run("cat << EOS > local_settings.py\n" + file_contents + "EOS", echo=False)
        ctx.run('git checkout {}'.format(ctx.config.host.branch))
        ctx.run("virtualenv venv")
        with ctx.prefix("source venv/bin/activate"):
            ctx.run('pip3 install -r requirements.txt')
            ctx.run('python3 manage.py migrate')
            ctx.run('python3 manage.py collectstatic --noinput')
            if(initial):
                ctx.run('python3 manage.py loaddata initial_hunt')

        ctx.run('mkdir -p ./media/puzzles')
        ctx.run('mkdir -p ./media/prepuzzles')
    ctx.sudo('chgrp -R www-data {}/media'.format(project_folder))
    ctx.sudo('chmod -R go+r {}'.format(project_folder))
    ctx.sudo('chmod -R og+rw {}/media'.format(project_folder))

    # Populate and put apache config file in place
    apache_path = "/etc/apache2/sites-enabled/{}.conf".format(project_name)
    ctx.sudo('sh -c \'sed "s#replacepath#{}#g;s#replacename#{}#g" {}/config/{} > {}\''.format(
        project_folder, hostname, project_folder, apache_file, apache_path))
    if(ssl):
        ctx.sudo("certbot --apache -n --agree-tos --email {} --domains {}".format(
            contact_email, hostname))
    ctx.sudo('service apache2 restart')

    with ctx.cd(project_folder):
        test(ctx)

    # Tell sentry that we deployed


@task
def install(ctx, ssl=False):
    # Need git to kick off the process
    apt_check = ctx.sudo('apt --version', warn=True)
    if(apt_check.failed):
        print("This task only works on systems with apt based package management")
        sys.exit(1)
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
    ctx.sudo('apt-get install -y python3-dev python3-mysqldb python3-pip')
    ctx.sudo('pip3 install virtualenv')

    # Install apache and related
    ctx.sudo('apt-get install -y apache2 libapache2-mod-xsendfile libapache2-mod-wsgi-py3')
    # Apache hosting setup
    ctx.sudo('a2enmod proxy')
    ctx.sudo('a2enmod proxy_http')
    ctx.sudo('a2enmod proxy_html')
    ctx.sudo('a2enmod xsendfile')
    ctx.sudo('a2enmod wsgi')
    ctx.sudo("rm -f /etc/apache2/sites-enabled/*")

    # Set up a certificate using lets-encrypt
    if(ssl):
        ctx.sudo('apt-get install -y certbot python-certbot-apache')

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

    deploy(ctx, ssl=ssl)


@task
def release(ctx, version=None):
    if(version is None):
        print("No version argument given. Exiting.")
        sys.exit(1)

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
    - Modify deploy to use any apache config
    - Include shibboleth in deploy and install tasks 
    - Include ssl certs in install task 
    - Add checks to deploy to make sure we're not deploying broken code
    - Write backup-db and status
"""
