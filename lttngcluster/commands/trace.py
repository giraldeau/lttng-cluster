import argparse
from fabric.api import run, env
from fabric.network import disconnect_all
import pprint
import string

from lttngcluster.api import TraceRunner, TraceExperimentOptions
from lttngcluster.commands.base import BaseCommand
from lttngcluster.experiments.reg import registry
from lttngcluster.experiments.shell import TraceExperimentShell

def cmd_trace_command(args):
    cmd = " ".join(args.script)
    exp = TraceExperimentShell()
    exp.set_options({'command': cmd})
    runner = TraceRunner(exp)
    runner.run()

def cmd_trace_recipe(args):
    recipe = args.script[0]
    opts = TraceExperimentOptions()
    opts.load_path(recipe)
    if args.verbose:
        print('recipe:')
        pprint.pprint(opts)
    exp_class = opts.get('experiment', None)
    if exp_class:
        exp_instance = registry.get_experiment(exp_class)
        exp_instance.set_options(opts)
        exp_instance.action()

def cmd_trace_destroy(args):
    run("lttng destroy -a")

class TraceCommand(BaseCommand):
    actions = {
        'command': cmd_trace_command,
        'destroy': cmd_trace_destroy,
        'recipe': cmd_trace_recipe,
    }
    def arguments(self, parser):
        parser.add_argument('action', choices=self.actions.keys(), help='install action');
        parser.add_argument("script", nargs=argparse.REMAINDER)

    def handle(self, args):
        if args.hosts:
            env.hosts = string.split(args.hosts, ',')
        env.user = args.user
        exe = self.actions[args.action]
        try:
            exe(args)
        except KeyboardInterrupt:
            print("Abort")
        finally:
            disconnect_all()
