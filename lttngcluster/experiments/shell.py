from fabric.operations import local

from lttngcluster.api import TraceExperiment
from lttngcluster.experiments.reg import registry

class TraceExperimentShell(TraceExperiment):
    def __init__(self):
        super(TraceExperimentShell, self).__init__()
    def action(self):
        cmd = self.get_options().get('command', None)
        if cmd:
            local(cmd)

registry.register(TraceExperimentShell)