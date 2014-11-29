# -*- coding: utf-8 -*-

import gxf
import gdb

@gxf.register()
class Registers(gxf.DataCommand):
    '''
    Shows registers.
    '''

    def setup(self, parser):
        pass

    def run(self, args):

        regs = gxf.Registers()
        memory = gxf.Memory()

        for reg, val in regs.regs.items():
            if reg == "eflags" or (len(reg) == 2 and reg[1] == "s"):
                continue

            print("%-4s: " % reg, end="")

            memory.refchain(val).output()
