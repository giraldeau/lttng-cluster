
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
