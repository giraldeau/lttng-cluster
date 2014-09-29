import argparse
from fabric.network import disconnect_all
from fabric.state import env
from os.path import exists
import pprint

from lttngcluster.api import TraceRunnerDefault, TraceExperimentOptions, \
    RecipeErrorCollection
from lttngcluster.commands.base import BaseCommand
from lttngcluster.experiments.reg import registry
from lttngcluster.experiments.shell import TraceExperimentShell


def recipe_verify(recipe, err):
    opts = TraceExperimentOptions(**TraceExperimentOptions.default_options)
    opts.load_path(recipe)
    klass = registry.get_experiment(opts['experiment'])
    klass.set_options(opts)
    klass.validate(err)

def recipe_errors_show(recipe, errors):
    if len(errors) == 0:
        print('PASS: %s' % repr(recipe))
    else:
        print('FAIL: %s' % repr(recipe))
        for e in errors.errors:
            print('\terror: %s' % e)

def cmd_validate(args):
    for recipe in args.recipe:
        err = RecipeErrorCollection()
        recipe_verify(recipe, err)
        recipe_errors_show(recipe, err)

def cmd_trace_one(args, recipe):
    err = RecipeErrorCollection()
    opts = TraceExperimentOptions(**TraceExperimentOptions.default_options)
    opts.load_path(recipe)
    klass = registry.get_experiment(opts['experiment'])
    klass.set_options(opts)
    klass.validate(err)
    if len(err) > 0:
        pprint.pprint(opts)
        recipe_errors_show(recipe, err)
        raise Exception('validation error')
    if args.verbose:
        print('recipe:')
        pprint.pprint(opts)
    runner = TraceRunnerDefault()
    runner.set_dry_run(args.dry_run)
    runner.run(klass)

def cmd_trace(args):
    if len(args.recipe) == 0:
        raise Exception('Need a recipe file')
    for recipe in args.recipe:
        if not exists(recipe):
            raise Exception('File not found: %s' % recipe)
        cmd_trace_one(args, recipe)

def cmd_setup(args):
    raise NotImplementedError('TODO')

class RecipeCommand(BaseCommand):
    actions = {
        'validate': cmd_validate,
        'trace': cmd_trace,
        # 'setup': cmd_setup,
    }
    def arguments(self, parser):
        parser.add_argument('action', choices=self.actions.keys(), help='install action');
        parser.add_argument('recipe', nargs=argparse.REMAINDER)
        parser.add_argument('--dry-run', '-n', action='store_true', help='execute action without tracing')

    def handle(self, args):
        env.abort_on_prompts = True
        exe = self.actions[args.action]
        try:
            exe(args)
        except KeyboardInterrupt:
            print('Abort')
        finally:
            disconnect_all()
