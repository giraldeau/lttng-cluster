from lttngcluster.commands.base import BaseCommand

from fabric.api import task, run, parallel, execute, sudo, cd, env
#from fabric.decorators import with_settings

import string

@task
@parallel
def install_tools():
    sudo("apt-get install -y software-properties-common")
    sudo("apt-get update -q")
    sudo("apt-get upgrade -q -y")
    sudo("apt-get install -y lttng-tools babeltrace")
    sudo("apt-get install -y make gcc unzip wget git")

@task
@parallel
def install_addons():
    run("test -e ~/lttng-modules || git clone https://github.com/giraldeau/lttng-modules.git")
    with cd("~/lttng-modules"):
        run("git checkout addons")
        run("git pull")
        run("make -j4")
        sudo("make modules_install")
        sudo("mkdir -p /usr/local/bin/")
        sudo("install control-addons.sh /usr/local/bin")
    sudo("echo 'search extra updates ubuntu built-in' > /etc/depmod.d/ubuntu.conf")
    sudo("depmod -a")

@task
@parallel
def reload_daemon():
    sudo("control-addons.sh unload")
    sudo("service lttng-sessiond restart")
    sudo("control-addons.sh load")

@task
@parallel
def check():
    sudo("lttng list -k | grep sched_ttwu")

@task
@parallel
def reboot():
    sudo("reboot")

actions = {
    'tools': install_tools,
    'addons': install_addons,
    'reload': reload_daemon,
    'check': check,
    'reboot': reboot,
}

class InstallCommand(BaseCommand):
    def arguments(self, parser):
        parser.add_argument('action', choices=actions.keys(), help='install action');
    def handle(self, args):
        hosts_list = string.split(args.hosts[0], ',')
        exe = actions[args.action]
        env.user=args.user
        execute(exe, hosts=hosts_list)
