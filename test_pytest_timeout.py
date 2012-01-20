import os
import os.path
import signal
import threading

import pytest


pytest_plugins = 'pytester'


# This is required since our tests run py.test in a temporary
# directory and that py.test process needs to find the pytest_timeout
# module on it's sys.path.
os.environ['PYTHONPATH'] = os.path.dirname(__file__)


have_sigalrm = pytest.mark.skipif('not hasattr(signal, "SIGALRM")')


def pytest_funcarg__testdir(request):
    """pytester testdir funcarg with pytest_timeout in the plugins

    This has the effect of adding "-p pytest_timeout" to the py.test
    call of .runpytest() which is required for the --timeout parameter
    to work.
    """
    testdir = request.getfuncargvalue('testdir')
    testdir.plugins.append('pytest_timeout')
    return testdir


@have_sigalrm
def test_sigalrm(testdir):
    testdir.makepyfile("""
        import time

        def test_foo():
            time.sleep(2)
     """)
    result = testdir.runpytest('--timeout=1')
    result.stdout.fnmatch_lines([
            '*Failed: Timeout >1s*'
            ])


def test_thread(testdir, monkeypatch):
    testdir.makepyfile("""
        import time

        def test_foo():
            time.sleep(2)
    """)
    result = testdir.runpytest('--timeout=1', '--nosigalrm')
    result.stderr.fnmatch_lines([
            '*++ timeout ++*',
            '*-- stack of MainThread* --*',
            '*File *, line *, in *',
            '*++ timeout ++*',
            ])
    assert result.stderr.lines[-1] == '+' * 10 + ' timeout ' + '+' * 10
