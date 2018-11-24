from setuptools import setup

setup(
    name='pygments_pytest',
    description='A pygments lexer for pytest output.',
    url='https://github.com/asottile/pygments-pytest',
    version='1.0.2',
    author='Anthony Sottile',
    author_email='asottile@umich.edu',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    install_requires=['pygments'],
    py_modules=['pygments_pytest'],
    entry_points={'pygments.lexers': ['pytest=pygments_pytest:PytestLexer']},
)
