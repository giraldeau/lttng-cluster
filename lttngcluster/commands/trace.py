import argparse
from fabric.api import run, env
from fabric.network import disconnect_all
from os.path import exists
import pprint
import string

from lttngcluster.api import TraceRunnerDefault, TraceExperimentOptions, \
    RecipeErrorCollection
from lttngcluster.commands.base import BaseCommand
from lttngcluster.experiments.reg import registry
from lttngcluster.experiments.shell import TraceExperimentShell


def cmd_trace_command(args):
    cmd = " ".join(args.script)
    exp = TraceExperimentShell()
    exp.set_options({'command': cmd})
    runner = TraceRunnerDefault(exp)
    runner.run()

def cmd_trace_recipe(args):
    if len(args.script) == 0:
        raise Exception('Need a recipe file')
    recipe = args.script[0]
    if not exists(recipe):
        raise Exception('File not found: %s' % recipe)
    opts = TraceExperimentOptions()
    opts.load_path(recipe)
    if args.verbose:
        print('recipe:')
        pprint.pprint(opts)
    # set the environment
    if args.hosts:
        env.hosts = string.split(args.hosts, ',')
    env.user = opts.get('username', args.user)
    exp_class = opts.get('experiment', None)
    if exp_class:
        exp_instance = registry.get_experiment(exp_class)
        exp_instance.set_options(opts)
        err = RecipeErrorCollection()
        exp_instance.validate(err)
        if len(err) > 0:
            pprint.pprint(err)
            raise Exception("validation error")
        runner = TraceRunnerDefault()
        runner.run(exp_instance)

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
        exe = self.actions[args.action]
        try:
            exe(args)
        except KeyboardInterrupt:
            print('Abort')
        finally:
            disconnect_all()
