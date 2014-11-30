import argparse
import string
from fabric.api import env, execute
from fabric.network import disconnect_all

class BaseCommand(object):
    """
    Base class for commands. See django.core.management.base.BaseCommand
    """
    help = 'base command'
    def arguments(self, parser):
        pass
    def usage(self):
        pass
    def handle(self, args):
        raise NotImplementedError()

class ActionCommand(object):
    actions = {}

    def arguments(self, parser):
        parser.add_argument('-r', '--remotes', type=str, help='comma-separated list of remote hosts on which to execute the command')
        parser.add_argument('-u', '--user', type=str, help='user that will execute the command on the remote hosts')
        parser.add_argument('action', choices=self.actions.keys(), help='install action');
        parser.add_argument("script", nargs=argparse.REMAINDER)

    def handle(self, args):
        print repr(args)
        remotes_list = string.split(args.remotes, ',')
        exe = self.actions[args.action]
        env.user=args.user
        try:
            execute(exe, args, hosts=remotes_list)
        except KeyboardInterrupt:
            print("Abort")
        finally:
            disconnect_all()