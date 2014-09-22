
def setup():
    pass

def teardown():
    pass

def test_load_script():
    from lttngcluster.commands import install
    cases = [ 'scripts/install-client.sh',
              'http://google.com',
              'https://google.com' ]
    for case in cases:
        cnt = install.load_script(case)
        assert len(cnt) > 0

def test_register_experiment():
    from lttngcluster.experiments import registry
    from lttngcluster.api import TraceExperiment
    from lttngcluster.experiments import AlreadyRegistered, NotRegistered

    class TestExperiment(TraceExperiment):
        pass

    registry.register(TestExperiment)
    exp = registry.get_experiment('TestExperiment')
    exception1 = None
    exception2 = None
    try:
        registry.register(TestExperiment)
    except Exception as e:
        exception1 = e
    try:
        registry.get_experiment('bidon')
    except Exception as e:
        exception2 = e

    assert isinstance(exp, TraceExperiment)
    assert isinstance(exception1, AlreadyRegistered)
    assert isinstance(exception2, NotRegistered)
