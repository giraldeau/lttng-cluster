from lttngcluster.commands.base import BaseCommand
from lttngcluster.api import TraceExperimentSimple, TraceRunner
from fabric.api import run, env
import argparse

import string
from fabric.network import disconnect_all

def cmd_trace_experiment(args):
    cmd = " ".join(args.script)
    exp = TraceExperimentSimple(cmd)
    runner = TraceRunner(exp)
    runner.run()

def cmd_trace_destroy(args):
    run("lttng destroy -a")

class TraceCommand(BaseCommand):
    actions = {
        'experiment': cmd_trace_experiment,
        'destroy': cmd_trace_destroy,
    }
    def arguments(self, parser):
        parser.add_argument('action', choices=self.actions.keys(), help='install action');
        parser.add_argument("script", nargs=argparse.REMAINDER)

    def handle(self, args):
        env.hosts = string.split(args.hosts, ',')
        env.user = args.user
        exe = self.actions[args.action]
        try:
            exe(args)
        except KeyboardInterrupt:
            print("Abort")
        finally:
            disconnect_all()