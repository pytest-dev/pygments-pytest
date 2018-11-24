import os.path
import re

import pygments.lexer
import pygments.token

Color = pygments.token.Token.Color


class PytestLexer(pygments.lexer.RegexLexer):
    name = 'pytest'
    aliases = ('pytest',)
    flags = re.MULTILINE

    def filename_line(self, match):
        yield match.start(1), Color.BoldRed, match.group(1)
        yield match.start(2), pygments.token.Text, match.group(2)

    tokens = {
        'root': [
            (r'^=+ test session starts =+$', Color.Bold),
            (r'^collecting \.\.\.', Color.Bold),
            (r'[^ \n]+(?=.*\[ *\d+%\])', pygments.token.Text, 'progress_line'),
            (r'^=+ (ERRORS|FAILURES) =+$', pygments.token.Text, 'failures'),
            (r'^=+ warnings summary( \(final\))? =+$', Color.Yellow),
            (r'^=+ [1-9]\d* (failed|error).*=+$', Color.BoldRed),
            (r'^=+ .*[1-9]\d* warnings.*=+$', Color.BoldYellow),
            (r'^=+ [1-9]\d* passed.*=+$', Color.BoldGreen),
            (r'^=+ [1-9]\d* (deselected|skipped).*=+$', Color.BoldYellow),
            (r'^=+ [1-9]\d* (xfailed|xpassed).*=+$', Color.BoldYellow),
            (r'^=+ no tests ran.*=+$', Color.BoldYellow),
            (r'.', pygments.token.Text),  # prevent error tokens
        ],
        'progress_line': [
            (r'PASSED|\.', Color.Green),
            (r'SKIPPED|XPASS|xfail|s|X|x', Color.Yellow),
            (r'ERROR|FAILED|E|F', Color.Red),
            (r'\[ *\d+%\]', Color.Cyan),
            (r' +', pygments.token.Text),
        ],
        'failures': [
            (r'(?=^=+ )', pygments.token.Text, '#pop'),

            (r'^_+ .+ _+$', Color.BoldRed),
            (r'^E .*$', Color.BoldRed),
            (r'^(<[^>\n]+>|[^:\n]+)(:\d+:.*$)', filename_line),
            (r'^(    |>).+$', Color.Bold),
            # otherwise pygments will reset our state machine to `root`
            (r'\n', pygments.token.Text),
            (r'.', pygments.token.Text),  # prevent error tokens
        ],
    }


COLORS = {
    'Cyan': '#06989a', 'Green': '#4e9a06', 'Red': '#c00', 'Yellow': '#c4A000',
}


def stylesheet(colors=None):
    colors = colors or {}
    assert set(colors) <= set(COLORS), set(colors) - set(COLORS)
    return '.-Color-Bold { font-weight: bold; }' + ''.join(
        '.-Color-Bold{k}{{ color: {v}; font-weight: bold; }}\n'
        '.-Color-{k}{{ color: {v}; }}\n'.format(k=k, v=colors.get(k, v))
        for k, v in sorted(COLORS.items())
    )


def setup(app):  # pragma: no cover (sphinx)
    def add_stylesheet(app):
        app.add_stylesheet('pygments_pytest.css')

    def copy_stylesheet(app, exception):
        if app.builder.name != 'html' or exception:
            return

        path = os.path.join(app.builder.outdir, '_static/pygments_pytest.css')
        with open(path, 'w') as f:
            f.write(stylesheet(app.config.pygments_pytest_ansi_colors))

    app.require_sphinx('1.0')
    app.add_config_value('pygments_pytest_ansi_colors', {}, 'html')
    app.connect('builder-inited', add_stylesheet)
    app.connect('build-finished', copy_stylesheet)
