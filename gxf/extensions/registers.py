# -*- coding: utf-8 -*-

import gxf

from gxf.formatting import Token, Formattable


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

            if reg in ("rdi", "rsi", "rdx", "rcx", "r8", "r9"):
                ttype = Token.Text
            elif reg in ("rip", "rbp", "rsp"):
                ttype = Token.Generic.Heading
            else:
                ttype = Token.Comment

            print("%s%s" % (
                    Formattable(((ttype, "%-4s" % reg),
                                 (Token.Comment, ": "))),
                    memory.refchain(val)))
