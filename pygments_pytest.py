import re

import pygments.lexer
import pygments.token

Color = pygments.token.Token.Color


class PytestLexer(pygments.lexer.RegexLexer):
    name = 'pytest'
    aliases = ('pytest',)
    flags = re.MULTILINE

    def filename_line(self, match):
        filename, colon, rest = match.group().partition(':')
        yield match.start(), Color.BoldRed, filename
        yield match.start() + len(filename), pygments.token.Text, colon + rest

    tokens = {
        'root': [
            (r'^=+ test session starts =+$', Color.Bold),
            (r'^collecting \.\.\.', Color.Bold),
            (r'[^ \n]+(?=.*\[ *\d+%\])', pygments.token.Text, 'progress_line'),
            (r'^=+ (ERRORS|FAILURES) =+$', pygments.token.Text, 'failures'),
            (r'^=+ warnings summary =+$', Color.Yellow),
            (r'^=+ [1-9]\d* (failed|error).*=+$', Color.BoldRed),
            (r'^=+ .*[1-9]\d* warnings.*=+$', Color.BoldYellow),
            (r'^=+ [1-9]\d* passed.*=+$', Color.BoldGreen),
            (r'^=+ [1-9]\d* deselected.*=+$', Color.BoldYellow),
            (r'^=+ no tests ran.*=+$', Color.BoldYellow),
        ],
        'progress_line': [
            (r'PASSED|\.', Color.Green),
            (r'SKIPPED|XPASS|xfail|s|X|x', Color.Yellow),
            (r'ERROR|FAILED|E|F', Color.Red),
            (r'\[ *\d+%\]', Color.Cyan),
            (r' +', pygments.token.Text),
        ],
        'failures': [
            # note: ____ ERROR at setup of ... ____ is not red
            (r'^_+ ((?!ERROR ).+) _+$', Color.BoldRed),

            (r'^E .*$', Color.BoldRed),
            (r'^[^:\n]+:\d+:.*$', filename_line),
            (r'^(    |>).+$', Color.Bold),
            # otherwise pygments will reset our state machine to `root`
            (r'\n', pygments.token.Text),
            (r'(?=^=+ )', pygments.token.Text, '#pop'),
        ],
    }
