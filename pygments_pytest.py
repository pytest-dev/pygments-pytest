import os.path
import re
from typing import Any
from typing import Dict
from typing import Generator
from typing import Match
from typing import Optional
from typing import Tuple

import pygments.lexer
import pygments.token

Tok = Tuple[int, Any, str]

Color = pygments.token.Token.Color
STATUSES = ('failed', 'passed', 'skipped', 'deselected', 'no tests ran')
BOLDIFY = {
    Color.Red: Color.Bold.Red,
    Color.Green: Color.Bold.Green,
    Color.Yellow: Color.Bold.Yellow,
}


class PytestLexer(pygments.lexer.RegexLexer):
    name = 'pytest'
    aliases = ('pytest',)
    flags = re.MULTILINE

    def filename_line(self, match: Match[str]) -> Generator[Tok, None, None]:
        yield match.start(1), Color.Bold.Red, match[1]
        yield match.start(2), pygments.token.Text, match[2]

    def status_line(self, match: Match[str]) -> Generator[Tok, None, None]:
        if match['failed'] or match['errors']:
            start_end_color = Color.Red
        elif (
                match['skipped'] or
                match['xfailed'] or
                match['xpassed'] or
                match['warnings']
        ):
            start_end_color = Color.Yellow
        else:
            start_end_color = Color.Green

        if match['before']:
            yield match.start('before'), start_end_color, match['before']
        for k, color in (
                ('failed', Color.Red),
                ('passed', Color.Green),
                ('skipped', Color.Yellow),
                ('deselected', Color.Yellow),
                ('xfailed', Color.Yellow),
                ('xpassed', Color.Yellow),
                ('warnings', Color.Yellow),
                ('errors', Color.Red),
        ):
            if color == start_end_color:
                color = BOLDIFY[color]
            kcomma = f'{k}comma'
            if match[k]:
                yield match.start(k), color, match[k]
            if match[kcomma]:
                yield match.start(kcomma), pygments.token.Text, match[kcomma]
        yield match.start('time'), start_end_color, match['time']
        if match['after']:
            yield match.start('after'), start_end_color, match['after']

    tokens = {
        'root': [
            (r'^=+ test session starts =+$', Color.Bold),
            (r'^collecting \.\.\.', Color.Bold),
            (r'^(?=.+\[ *\d+%\]$)', pygments.token.Text, 'progress_line'),
            (r'^=+ (ERRORS|FAILURES) =+$', pygments.token.Text, 'failures'),
            (r'^=+ warnings summary( \(final\))? =+$', Color.Yellow),
            (
                r'^(?P<before>=+ )?'
                r'(?P<failed>\d+ failed)?(?P<failedcomma>, )?'
                r'(?P<passed>\d+ passed)?(?P<passedcomma>, )?'
                r'(?P<skipped>\d+ skipped)?(?P<skippedcomma>, )?'
                r'(?P<deselected>\d+ deselected)?(?P<deselectedcomma>, )?'
                r'(?P<xfailed>\d+ xfailed)?(?P<xfailedcomma>, )?'
                r'(?P<xpassed>\d+ xpassed)?(?P<xpassedcomma>, )?'
                r'(?P<warnings>\d+ warnings?)?(?P<warningscomma>, )?'
                r'(?P<errors>\d+ errors?)?(?P<errorscomma>)?'
                r'(?P<time> in [\d.]+s)'
                r'(?P<after> =+)?$',
                status_line,
            ),
            (r'^(=+ )?no tests ran.*(=+)?$', Color.Yellow),
            (r'.', pygments.token.Text),  # prevent error tokens
        ],
        'progress_line': [
            (r'^[^ ]+ (?=[^ \n]+ +\[)', pygments.token.Text),
            (r'PASSED|\.', Color.Green),
            (r' +', pygments.token.Text),
            (r'\n', pygments.token.Text, '#pop'),
        ],
        'failures': [
            (r'(?=^=+ )', pygments.token.Text, '#pop'),
            (
                r'(?=^[1-9]\d* ({}))'.format('|'.join(STATUSES)),
                pygments.token.Text,
                '#pop',
            ),

            (r'^_+ .+ _+$', Color.Bold.Red),
            (r'^E .*$', Color.Bold.Red),
            (r'^(<[^>\n]+>|[^:\n]+)(:\d+:.*$)', filename_line),
            (r'^(    |>).+$', Color.Bold),
            # otherwise pygments will reset our state machine to `root`
            (r'\n', pygments.token.Text),
            (r'.', pygments.token.Text),  # prevent error tokens
        ],
    }

    # the progress percentage is annoyingly stateful
    _PROGRESS = (r'^(?=.+\[ *\d+%\]$)', pygments.token.Text)
    _WARN = (r'SKIPPED|XPASS|XFAIL|xfail|s|X|x', Color.Yellow)
    _WARN_P = (*_WARN, ('root_w', 'progress_line_w'))
    _ERR = (r'ERROR|FAILED|E|F', Color.Red)
    _ERR_P = (*_ERR, ('root_e', 'progress_line_e'))
    _PERCENT = r'\[ *\d+%\]'

    tokens['root_w'] = list(tokens['root'])
    tokens['root_e'] = list(tokens['root'])

    tokens['root'].insert(0, (*_PROGRESS, 'progress_line'))
    tokens['root_w'].insert(0, (*_PROGRESS, 'progress_line_w'))
    tokens['root_e'].insert(0, (*_PROGRESS, 'progress_line_e'))

    tokens['progress_line_w'] = list(tokens['progress_line'])
    tokens['progress_line_e'] = list(tokens['progress_line'])

    tokens['progress_line'].extend((_WARN_P, _ERR_P, (_PERCENT, Color.Green)))
    tokens['progress_line_w'].extend((_WARN, _ERR_P, (_PERCENT, Color.Yellow)))
    tokens['progress_line_e'].extend((_WARN, _ERR, (_PERCENT, Color.Red)))


COLORS = {'Green': '#4e9a06', 'Red': '#c00', 'Yellow': '#c4a000'}


def stylesheet(colors: Optional[Dict[str, str]] = None) -> str:
    colors = colors or {}
    assert set(colors) <= set(COLORS), set(colors) - set(COLORS)
    return '.-Color-Bold { font-weight: bold; }\n' + ''.join(
        '.-Color-Bold-{k}{{ color: {v}; font-weight: bold; }}\n'
        '.-Color-{k}{{ color: {v}; }}\n'.format(k=k, v=colors.get(k, v))
        for k, v in sorted(COLORS.items())
    )


def setup(app: Any) -> None:  # pragma: no cover (sphinx)
    def copy_stylesheet(app: Any, exception: Optional[Exception]) -> None:
        if exception:
            return

        path = os.path.join(app.builder.outdir, '_static/pygments_pytest.css')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(stylesheet(app.config.pygments_pytest_ansi_colors))

    app.require_sphinx('1.0')
    app.add_config_value('pygments_pytest_ansi_colors', {}, 'html')
    app.add_stylesheet('pygments_pytest.css')
    app.connect('build-finished', copy_stylesheet)
