import argparse
import os

from lttngcluster.commands.install import InstallCommand
from lttngcluster.commands.trace import TraceCommand

cmds = {
    'install': InstallCommand(),
    'trace': TraceCommand(),
}

def main():
    parser = argparse.ArgumentParser(description='LTTng Cluster')
    parser.add_argument('-H', '--hosts', dest='hosts',
                        metavar='HOST', type=str, help='hosts string')
    parser.add_argument('-u', '--user', dest='user',
                        default=os.getlogin(), metavar='USER',
                        type=str, help='connection username')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true', default=False,
                        help='verbose mode')
    sub = parser.add_subparsers(help="sub-command help");
    for cmd in cmds.keys():
        p = sub.add_parser(cmd, help="command %s" % (cmd))
        handler = cmds[cmd]
        handler.arguments(p)
        p.set_defaults(obj=handler)
    args = parser.parse_args()
    args.obj.handle(args)
