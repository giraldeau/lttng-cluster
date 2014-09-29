import argparse

from lttngcluster.commands.install import InstallCommand
from lttngcluster.commands.recipe import RecipeCommand


cmds = {
    'install': InstallCommand(),
    'recipe': RecipeCommand(),
}

def main():
    parser = argparse.ArgumentParser(description='LTTng Cluster')
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
