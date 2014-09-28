# Experiment registration, similar to Django model admin registration
class AlreadyRegistered(Exception):
    pass

class NotRegistered(Exception):
    pass

class ExperimentRegistry(object):

    def __init__(self):
        self._registry = {}  # class_name -> exp_class

    def register(self, exp_class):
        if (exp_class.__name__ in self._registry):
            raise AlreadyRegistered('The experiment %s is already registered' % exp_class.__name__)
        self._registry[exp_class.__name__] = exp_class()

    def get_experiment(self, name):
        if (name not in self._registry):
            raise NotRegistered('The experiment %s is not registered' % name)
        return self._registry[name]

    def experiments(self):
        return self._registry

registry = ExperimentRegistry()
