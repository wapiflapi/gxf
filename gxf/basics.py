# -*- coding: utf-8 -*-

import gdb
import gxf

debug = False


def execute(cmd, tty=False, tostr=True):

    if debug:
        print("[debug] execute: %s" % cmd)

    try:
        return gdb.execute(cmd, tty, tostr)
    except gdb.MemoryError as e:
        raise gxf.MemoryError(e)


def parse_and_eval(*args, **kwargs):
    if debug:
        print("[debug] pae: %s %s" % (args, kwargs))

    try:
        return gdb.parse_and_eval(*args, **kwargs)
    except gdb.MemoryError as e:
        raise gxf.MemoryError(e)

class Expression(gxf.Formattable):

    def __init__(self, expression):
        self.tokens = []
        if isinstance(expression, list):
            self.tokens = expression
            self.text = "".join(v for t, v in expression)
        elif expression:
            self.text = expression
            raise NotImplementedError("Can't create Expression from text yet.")

    def fmttokens(self):
        yield from self.tokens

    def eval(self):
        return parse_and_eval(self.text)
