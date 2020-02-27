import os.path
import re
import shlex

import pygments.formatters
import pygments.lexers
import pytest

import pygments_pytest

ANSI_LEXER = pygments.lexers.get_lexer_by_name('ansi', stripnl=False)
PYTEST_LEXER = pygments.lexers.get_lexer_by_name('pytest', stripnl=False)
HTML_FORMATTER = pygments.formatters.HtmlFormatter()

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


def uncolor(s):
    return ANSI_ESCAPE.sub('', s)


def highlight(lexer, s):
    ret = pygments.highlight(s, lexer=lexer, formatter=HTML_FORMATTER)
    ret = NORM_WS_START_RE.sub(r'\2\1', ret)
    ret = NORM_WS_END_RE.sub(r'\2\1', ret)
    ret = EMPTY_TAG_RE.sub('', ret)
    return HTML.replace('HTML', ret)


@pytest.fixture(params=['', '-v', '-q'])
def compare(testdir, request):
    def compare_fn(src, args=()):
        testdir.tmpdir.join('f.py').write(src)

        args += ('f.py', '--color=yes') + tuple(shlex.split(request.param))
        ret = testdir.runpytest(*args)

        ansi = highlight(ANSI_LEXER, ret.stdout.str())
        pytest = highlight(PYTEST_LEXER, uncolor(ret.stdout.str()))

        fname = f'{request.node.name}_ansi.html'
        with open(os.path.join(DEMO_DIR, fname), 'w') as f:
            f.write(ansi)

        fname = f'{request.node.name}_pytest.html'
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
        '    pytest.raises(ValueError, "int(None)")\n',
    )


def test_blank_code_line(compare):
    compare(
        'def test():\n'
        '    \n'
        '    assert False\n',
    )


def test_only_skips(compare):
    compare(
        'import pytest\n'
        '@pytest.mark.skip\n'
        'def test(): pass\n',
    )


def test_only_xpass(compare):
    compare(
        'import pytest\n'
        '@pytest.mark.xfail\n'
        'def test(): pass\n',
    )


def test_only_xfail(compare):
    compare(
        'import pytest\n'
        '@pytest.mark.xfail\n'
        'def test():\n'
        '    assert False\n',
    )


@pytest.mark.xfail
def test_collection_failure_syntax_error(compare):
    compare('(')


@pytest.mark.xfail
def test_collection_unknown_fixture(compare):
    compare('def test(x): pass')
