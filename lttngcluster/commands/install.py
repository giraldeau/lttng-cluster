from lttngcluster.commands.base import BaseCommand

from fabric.api import task, run, parallel, execute, sudo, cd, env, settings, hide
from fabric.network import disconnect_all
#from fabric.decorators import with_settings

import os
import argparse
import string
import urllib2

default_script_url =  "https://raw.githubusercontent.com/giraldeau/lttng-cluster/master/scripts/install-client.sh"

def load_script(script):
    cnt = ""
    if (os.path.exists(script)):
        with open(script) as xfile:
            cnt = xfile.read()
    elif (script.startswith("http://") or
        script.startswith("https://")):
        response = urllib2.urlopen(script)
        cnt = response.read()
        response.close()
    else:
        raise IOError("script not found: %s" % script)
    return cnt

@task
@parallel
def runscript(args):
    fname = "install.sh"
    if len(args.script) == 0:
        raise RuntimeError("missing script")
    content = load_script(args.script[0])
    with cd("/tmp/"):
        with settings(hide('running')):
            run("echo '%s' > %s" % (content, fname))
        run("chmod +x %s" % (fname))
        opts = " ".join(args.script[1:])
        sudo("./%s %s" % (fname, opts))

@task
@parallel
def check(args):
    sudo("lttng list -k | grep sched_ttwu")

@task
@parallel
def reboot(args):
    sudo("reboot")

@task
def connect(args):
    sudo('date')

actions = {
    'runscript': runscript,
    'check': check,
    'reboot': reboot,
    'connect': connect,
}

class InstallCommand(BaseCommand):
    def arguments(self, parser):
        parser.add_argument('action', choices=actions.keys(), help='install action');
        parser.add_argument("script", nargs=argparse.REMAINDER)

    def handle(self, args):
        hosts_list = string.split(args.hosts, ',')
        exe = actions[args.action]
        env.user=args.user
        try:
            execute(exe, args, hosts=hosts_list)
        except KeyboardInterrupt:
            print("Abort")
        finally:
            disconnect_all()
