# -*- coding: utf-8 -*-

import traceback

from contextlib import contextmanager

import gdb
import gxf

GdbError = gdb.error


class MemoryError(gdb.MemoryError):
    def __init__(self, address, msg="Cannot access memory at address {:#x}"):

        if isinstance(address, gdb.MemoryError):
            address = int(str(address).rsplit(None, 1)[-1], 0)
            self.__cause__ = None

        self.address = address
        super().__init__(msg.format(int(self.address)))


def show_error(e):
    """
    Decorate a function so it masks tracebacks when debug=False
    """
    if gxf.basics.debug:
        # Gdb can't give us a full traceback. If this is a tty
        # or if error occured during argument parsing we do it.
        print("%s" % (traceback.format_exc(),), end="")
    print(e)
    if not gxf.basics.debug:
        print("    If that's weird check `python gxf.basics.debug = True`")


@contextmanager
def allow_errors():
    try:
        yield
    except BaseException as e:
        show_error(e)
