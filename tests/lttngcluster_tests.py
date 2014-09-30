from lttngcluster.api import default_trace_dir, RecipeErrorCollection
from lttngcluster.utils import DictCmpListener


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
    from lttngcluster.api import TraceExperiment
    from lttngcluster.experiments.reg import registry, AlreadyRegistered, NotRegistered

    class TestExperiment(TraceExperiment):
        def validate(self, errors):
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

def test_load_options():
    from lttngcluster.api import TraceExperimentOptions
    from lttngcluster.api import default_username

    override = 'foo'
    recipe = '''username: %s''' % (override)

    opts = TraceExperimentOptions(**TraceExperimentOptions.default_options)
    print(opts)
    assert opts['username'] == default_username
    opts.load(recipe)
    assert opts['username'] == override

def test_merge_dict():
    from lttngcluster.api import merge_dict

    dst = { 'a' : 'a', 'b': 'b', 'c': { 'a': 'a', 'b': 'b' } }
    src = { 'a' : 'x', 'd': 'x', 'c': { 'a': 'x', 'c': 'x' } }
    exp = { 'a' : 'x', 'b': 'b', 'c': { 'a': 'x', 'b': 'b', 'c': 'x' }, 'd': 'x' }
    merge_dict(dst, src)
    assert exp == dst

def test_load_include():
    from lttngcluster.api import TraceExperimentOptions
    import tempfile
    from os.path import join
    from shutil import rmtree

    content = { 'recipe_a.yaml': '''a: a\nb: b''',
                'recipe_b.yaml': '''import: recipe_a\nb: x\nz: z''',
                'recipe_c.yaml': '''import: recipe_b\nb: y\nc: c''',
    }
    exp = { 'a': 'a', 'b': 'y', 'c': 'c', 'z': 'z', 'name': 'recipe_c' }
    d = tempfile.mkdtemp()
    for k, v in content.items():
        with file(join(d, k), 'w+') as f:
            f.write(v)

    opts = TraceExperimentOptions()
    try:
        opts.load_path(join(d, 'recipe_c.yaml'))
    finally:
        rmtree(d)

    print(exp)
    print(opts)

    assert opts == exp

def test_trace_dir():
    from lttngcluster.api import TraceExperimentOptions
    import os
    opts = TraceExperimentOptions()

    data = { 'test1': { 'input': { }, 'exp': 'auto-ts' },
             'test2': { 'input': { 'foo': 'one', 'bar': 2 }, 'exp': 'auto-ts-foo=one-bar=2' }
    }

    opts._time = 'ts'
    for k, v in data.items():
        d = opts.get_trace_dir(**v['input'])
        print(d)
        assert d == os.path.join(default_trace_dir, v['exp'])

def test_recipe_validate():
    from lttngcluster.api import TraceExperimentOptions
    from lttngcluster.commands.recipe import recipe_verify, recipe_errors_show
    import pprint
    import os

    from lttngcluster.experiments.reg import registry

    expected = {
        'recipe_fail_key.yaml': 1,
        'recipe_fail_role.yaml': 3,
        'recipe_fail_type.yaml': 2,
    }

    for k, v in expected.items():
        err = RecipeErrorCollection()
        recipe = os.path.join('tests', 'cases', k)
        recipe_verify(recipe, err)
        recipe_errors_show(recipe, err)
        assert len(err) == v

class DictCmpListenerTest(DictCmpListener):
    def __init__(self):
        self.reset();
        super(DictCmpListenerTest, self).__init__()

    def missing(self, d1, d2, path):
        print('missing ' + repr(path))
        self._status['missing'].append(path)

    def present(self, d1, d2, path):
        print('present ' + repr(path))
        self._status['present'].append(path)

    def reset(self):
        self._status = { 'missing': [], 'present': [] }

def test_cmp_dict():
    from lttngcluster.utils import DictCmp
    check = DictCmpListenerTest()
    comparator = DictCmp()
    comparator.add_listener(check)

    d1 = { 'a': { 'b' : { 'c': 'd' } } }
    d2 = { 'a': { 'b' : { 'c': 'd' } } }
    d3 = { 'a': { 'b' : 'c' } }

    exp1 = { 'missing': [ ], 'present': [ ['a'], ['a', 'b'], ['a', 'b', 'c'] ] }
    exp2 = { 'missing': [ [ 'a', 'b', 'c' ] ], 'present': [ ['a'], ['a', 'b'] ] }

    data = [ (d1, d2, exp1), (d1, d3, exp2) ]

    for tup in data:
        (foo, bar, exp) = tup
        comparator.compare(foo, bar)
        assert check._status == exp
        check.reset()

def test_coerce_bool():
    from lttngcluster.utils import coerce_bool

    cases = [
        { 'input': True, 'exp': True },
        { 'input': False, 'exp': False },
        { 'input': 'true', 'exp': True },
        { 'input': 'yes', 'exp': True },
        { 'input': 'false', 'exp': False },
        { 'input': 'no', 'exp': False },
        { 'input': 1, 'exp': True },
        { 'input': 0, 'exp': False },
    ]

    for case in cases:
        assert coerce_bool(case['input']) == case['exp']

    exc = None
    try:
        coerce_bool('foo')
    except Exception as e:
        exc = e
    assert isinstance(exc, ValueError)