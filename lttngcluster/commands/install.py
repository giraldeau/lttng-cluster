from lttngcluster.commands.base import ActionCommand

from fabric.api import task, run, parallel, sudo, cd, settings, hide
from fabric.contrib import files
import os
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
        run("truncate -s 0 %s" % (fname))
        files.append(fname, content)
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

class InstallCommand(ActionCommand):
    actions = {
        'runscript': runscript,
        'check': check,
        'reboot': reboot,
        'connect': connect,
    }