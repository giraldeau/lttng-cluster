from fabric.operations import local

from lttngcluster.api import TraceExperiment
from lttngcluster.experiments.reg import registry

class TraceExperimentClientServerRequest(TraceExperiment):
    def __init__(self):
        super(TraceExperimentClientServerRequest, self).__init__()

    def validate(self, errors):
        pass

    def before(self):
        opts = self.get_options()
        opts.get('params', {}).get('start_server', None)
        pass

    def action(self):
        # make request
        pass

    def after(self):
        # stop server
        pass

registry.register(TraceExperimentClientServerRequest)
