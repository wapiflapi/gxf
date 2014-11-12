# -*- coding: utf-8 -*-

import gdb

GdbError = gdb.error

class MemoryError(gdb.MemoryError):
    def __init__(self, address, msg="Cannot access memory at address {:#x}"):

        if isinstance(address, gdb.MemoryError):
            address = int(str(address).rsplit(None, 1)[-1], 0)
            self.__cause__ = None

        self.address = address
        super().__init__(msg.format(self.address))



