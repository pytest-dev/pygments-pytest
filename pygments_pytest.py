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


class PytestLexer(pygments.lexer.RegexLexer):
    name = 'pytest'
    aliases = ('pytest',)
    flags = re.MULTILINE

    def filename_line(self, match: Match[str]) -> Generator[Tok, None, None]:
        yield match.start(1), Color.Bold.Red, match[1]
        yield match.start(2), pygments.token.Text, match[2]

    tokens = {
        'root': [
            (r'^=+ test session starts =+$', Color.Bold),
            (r'^collecting \.\.\.', Color.Bold),
            (r'^(?=.+\[ *\d+%\]$)', pygments.token.Text, 'progress_line'),
            (r'^=+ (ERRORS|FAILURES) =+$', pygments.token.Text, 'failures'),
            (r'^=+ warnings summary( \(final\))? =+$', Color.Yellow),
            (r'^(=+ )?[1-9]\d* (failed|error).*(=+)?$', Color.Bold.Red),
            (r'^(=+ )?[1-9].*[1-9]\d* warnings.*(=+)?$', Color.Bold.Yellow),
            (r'^(=+ )?[1-9]\d* passed.*(=+)?$', Color.Bold.Green),
            (
                r'^(=+ )?[1-9]\d* (deselected|skipped).*(=+)?$',
                Color.Bold.Yellow,
            ),
            (r'^(=+ )?[1-9]\d* (xfailed|xpassed).*(=+)?$', Color.Bold.Yellow),
            (r'^(=+ )?no tests ran.*(=+)?$', Color.Bold.Yellow),
            (r'.', pygments.token.Text),  # prevent error tokens
        ],
        'progress_line': [
            (r'^[^ ]+ (?=[^ \n]+ +\[)', pygments.token.Text),
            (r'PASSED|\.', Color.Green),
            (r'SKIPPED|XPASS|XFAIL|xfail|s|X|x', Color.Yellow),
            (r'ERROR|FAILED|E|F', Color.Red),
            (r'\[ *\d+%\]', Color.Cyan),
            (r' +', pygments.token.Text),
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


COLORS = {
    'Cyan': '#06989a', 'Green': '#4e9a06', 'Red': '#c00', 'Yellow': '#c4a000',
}


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
