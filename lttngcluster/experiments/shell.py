from fabric.api import run
from fabric.context_managers import settings
from fabric.operations import local, sudo
from fabric.state import env
from fabric.tasks import execute

from lttngcluster.api import TraceExperiment, run_foreground
from lttngcluster.experiments.reg import registry
from lttngcluster.utils import coerce_bool


class TraceExperimentShell(TraceExperiment):
    def __init__(self):
        super(TraceExperimentShell, self).__init__()

    def validate(self, err):
        recipe_required = {
            'roledefs': dict,
            'execute': list,
            'events': dict,
        }
        opts = self.get_options()
        for required, t in recipe_required.items():
            if not opts.has_key(required):
                err.add('missing parameter %s' % (required))
            elif type(opts.get(required)) is not t:
                err.add('wrong type %s' % (repr(t)))

        roledefs = opts.get('roledefs', {})
        execute_list = opts.get('execute', [])
        if isinstance(roledefs, dict) and isinstance(execute_list, list):
            for execute in execute_list:
                if not execute.has_key('roles'):
                    err.add('missing parameter roles: %s' % repr(execute))
                else:
                    roles = execute.get('roles', [])
                    if not hasattr(roles, '__iter__'):
                        roles = [roles]
                    for role in roles:
                        if role not in roledefs:
                            err.add('reference to undefined role: %s' % (role))
        ev = opts.get('events', {})
        for k, v in ev.items():
            if not isinstance(v, list):
                err.add('wrong type for event list %s: %s' % (k, type(v)))

    def action(self):
        opts = self.get_options()
        cmds = opts.get('execute', [])
        env.roledefs = opts['roledefs']
        for cmd in cmds:
            if not cmd.has_key('command') or \
                not isinstance(cmd.get('command'), str):
                raise ValueError('wrong command')
            use_sudo = coerce_bool(cmd.get('use_sudo', False))
            roles = cmd.get('roles', [])
            if not hasattr(roles, '__iter__'):
                roles = [roles]
            command = cmd.get('command')
            execute(run_foreground, command, roles=roles)

registry.register(TraceExperimentShell)
