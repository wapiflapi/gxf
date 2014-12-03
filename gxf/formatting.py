# -*- coding: utf-8 -*-

import abc

import pygments
from pygments.formatters import TerminalFormatter
from pygments.token import Token

formatter = TerminalFormatter(bg="dark")

class Formattable(object):

    def __init__(self, tokens=None):
        if tokens is not None:
            self._tokens = tokens

    def fmttokens(self):
        yield from self._tokens

    def format(self, *args, formatter=formatter, **kwargs):
        return pygments.format(self.fmttokens(*args, **kwargs), formatter)

    def output(self, *args, **kwargs):
        print(self.format(*args, **kwargs), end="\n")

    def __str__(self):
        return self.format()

    def __repr__(self):
        return self.format()
