class BaseCommand(object):
    """
    Base class for commands. See django.core.management.base.BaseCommand
    """
    help = 'base command'
    def arguments(self, args):
        pass
    def usage(self):
        pass
    def handle(self):
        raise NotImplementedError()