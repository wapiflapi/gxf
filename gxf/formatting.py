# -*- coding: utf-8 -*-

import abc

import pygments
from pygments.formatters import TerminalFormatter

formatter = TerminalFormatter(bg="dark")


class Formattable(object):

    @abc.abstractmethod
    def fmttokens(self):
        pass

    def format(self, *args, formatter=formatter, **kwargs):
        return pygments.format(self.fmttokens(*args, **kwargs), formatter)

    def output(self, *args, **kwargs):
        print(self.format(*args, **kwargs), end="")
