from fabric.operations import local

from lttngcluster.api import TraceExperiment
from lttngcluster.experiments.reg import registry
from lttngcluster.utils import recipe_verify

class TraceExperimentShell(TraceExperiment):
    def __init__(self):
        super(TraceExperimentShell, self).__init__()

    def validate(self, errors):
        required = { 'params': { 'target': None, 'command': None } }
        opts = self.get_options()
        recipe_verify(opts, required, errors)

    def action(self):
        cmd = self.get_options().get('command', None)
        if cmd:
            local(cmd)

registry.register(TraceExperimentShell)
