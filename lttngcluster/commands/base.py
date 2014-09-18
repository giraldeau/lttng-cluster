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
        parser.add_argument('action', choices=self.actions.keys(), help='install action');
        parser.add_argument("script", nargs=argparse.REMAINDER)

    def handle(self, args):
        hosts_list = string.split(args.hosts, ',')
        exe = self.actions[args.action]
        env.user=args.user
        try:
            execute(exe, args, hosts=hosts_list)
        except KeyboardInterrupt:
            print("Abort")
        finally:
            disconnect_all()