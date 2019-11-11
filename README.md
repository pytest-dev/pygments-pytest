[![Build Status](https://dev.azure.com/asottile/asottile/_apis/build/status/asottile.pygments-pytest?branchName=master)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=47&branchName=master)
[![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/asottile/asottile/47/master.svg)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=47&branchName=master)
[![Build Status](https://github.com/asottile/pygments-pytest/workflows/deploy/badge.svg)](https://github.com/asottile/pygments-pytest/actions)

pygments-pytest
===============

A pygments lexer for pytest output

See [some demos](https://asottile.github.io/pygments-pytest)!  Or
[see it in action on pytest.org](https://pytest.org).

## Installation

`pip install pygments-pytest`

## Usage

This library provides a pygments lexer called `pytest`.

```rst
.. code-block:: pytest

    $ pytest test.py
    ========================== test session starts ===========================
    platform linux -- Python 3.6.6, pytest-4.0.1.dev43+g0d529847.d20181123, py-1.7.0, pluggy-0.8.0
    rootdir: /home/asottile/workspace/pytest, inifile: tox.ini
    collected 1 item

    test.py .                                                          [100%]

    ======================== 1 passed in 0.01 seconds ========================
```

This library also provides a sphinx extension.  It can be enabled by adding
`'pygments_pytest'` to the `extensions` setting in your `conf.py`.

The colors can be tweaked using the sphinx setting (in `conf.py`)
`pygments_pytest_ansi_colors`:

```python
pygments_pytest_ansi_colors = {
    'Cyan': '#06989a',
    'Green': '#4e9a06',
    'Red': '#c00',
    'Yellow': '#c4A000',
}
```
