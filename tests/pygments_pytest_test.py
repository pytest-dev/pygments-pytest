import os.path
import re
import shlex
import subprocess
import sys

import importlib_metadata
import pygments.formatters
import pygments.lexers
import pytest

import pygments_pytest

ANSI_ESCAPE = re.compile(r'\033\[[^m]*m')
NORM_WS_START_RE = re.compile(r'(<[^/][^>]+>)(\s*)')
NORM_WS_END_RE = re.compile(r'(\s*)(</[^>]+>)')
EMPTY_TAG_RE = re.compile(r'<[^/][^>]+></[^>]+>')

DEMO_DIR = os.path.join(os.path.dirname(__file__), '../demo')

HTML = '''\
<!doctype html>
<html><head>
<style>body { background-color: #2d0922; color: #fff; } STYLES</style>
</head><body>HTML</body></html>
'''
HTML = HTML.replace('STYLES', pygments_pytest.stylesheet())


def test_versions():
    # When this fails, remove installation from `git` in requirements-dev.txt
    version = importlib_metadata.version('py')
    assert '+g' in version and version[:5] == '1.7.1'


def uncolor(s):
    return ANSI_ESCAPE.sub('', s)


def highlight(lang, s):
    lexer = pygments.lexers.get_lexer_by_name(lang, stripnl=False)
    formatter = pygments.formatters.HtmlFormatter()
    ret = pygments.highlight(s, lexer=lexer, formatter=formatter)
    ret = NORM_WS_START_RE.sub(r'\2\1', ret)
    ret = NORM_WS_END_RE.sub(r'\2\1', ret)
    ret = EMPTY_TAG_RE.sub('', ret)
    return HTML.replace('HTML', ret)


@pytest.fixture(params=['', '-v'])
def compare(tmpdir, request):
    def compare_fn(src, args=()):
        tmpdir.join('f.py').write(src)

        args += tuple(shlex.split(request.param))
        cmd = (sys.executable, '-mpytest', '--color=yes', 'f.py') + args
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=str(tmpdir))
        out, _ = proc.communicate()
        out = out.decode('UTF-8')

        ansi = highlight('ansi', out)
        pytest = highlight('pytest', uncolor(out))

        fname = '{}_ansi.html'.format(request.node.name)
        with open(os.path.join(DEMO_DIR, fname), 'w') as f:
            f.write(ansi)

        fname = '{}_pytest.html'.format(request.node.name)
        with open(os.path.join(DEMO_DIR, fname), 'w') as f:
            f.write(pytest)

        assert ansi == pytest

    return compare_fn


def test_simple_test_passing(compare):
    compare('def test(): pass')


def test_warnings(compare):
    compare(
        'import warnings\n'
        'def test():\n'
        '    warnings.warn(UserWarning("WARNING!"))\n',
    )


DIFFERENT_TYPES_SRC = '''\
import pytest

def inc(x):
    return x + 1

def test_answer():
    assert inc(3) == 5

def fail2():
    raise RuntimeError('error!')

def test_fail_stack():
    fail2()

def test(): pass

def test_skip():
    pytest.skip()

def test_xfail():
    pytest.xfail()

@pytest.mark.xfail
def test_Xxfail():
    pass

@pytest.fixture
def s():
    raise Exception('boom!')

def test_error(s):
    pass
'''


def test_different_test_types(compare):
    compare(DIFFERENT_TYPES_SRC)


def test_too_long_summary_line(compare):
    compare(DIFFERENT_TYPES_SRC, args=('-k', 'not stack'))


def test_no_tests(compare):
    compare('')


def test_deprecated_raises_exec_failure(compare):
    compare(
        'import pytest\n'
        'def test():\n'
        '    pytest.raises(ValueError, "int(None)")\n'
    )


def test_blank_code_line(compare):
    compare(
        'def test():\n'
        '    \n'
        '    assert False\n',
    )


@pytest.mark.xfail
def test_collection_failure_syntax_error(compare):
    compare('(')


@pytest.mark.xfail
def test_collection_unknown_fixture(compare):
    compare('def test(x): pass')
