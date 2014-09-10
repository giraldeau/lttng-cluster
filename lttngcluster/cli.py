import argparse
from lttngcluster.commands.install import InstallCommand
from lttngcluster.commands.trace import TraceCommand

cmds = {
    'install': InstallCommand,
    'trace': TraceCommand,
}

def main():
    parser = argparse.ArgumentParser(description='LTTng Cluster')
    parser.add_argument('cmd', choices=cmds.keys())
    args = parser.parse_args()
    print(args)
