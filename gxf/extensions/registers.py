# -*- coding: utf-8 -*-

import gxf

from gxf.formatting import Token, Formattable


@gxf.register()
class Registers(gxf.DataCommand):
    '''
    Shows registers.
    '''

    def setup(self, parser):
        parser.add_argument("-m", "--mark", action='append', default=[],
                            help="Highlight some registers.")
        parser.add_argument("-M", "--mark-used", action='store_true',
                            help="Highlight currently used registers.")

    def run(self, args):

        regs = gxf.Registers()
        memory = gxf.Memory()

        tomark = args.mark[:]

        if args.mark_used:
            try:
                dis = gxf.disassemble_lines(regs.get('pc')).lines[:1]
            except gxf.GdbError:
                dis = ()
            for line in dis:
                for _, t in line.tokens[line.instidx:]:
                    tomark.append(t)
                    tomark.extend(regs.impact.get(t, ()))

        for reg, val in regs.regs.items():
            if reg == "eflags" or (len(reg) == 2 and reg[1] == "s"):
                continue

            if reg in tomark:
                ttype = Token.Name.Builtin
            elif reg in ("rdi", "rsi", "rdx", "rcx", "r8", "r9"):
                ttype = Token.Text
            elif reg in ("rip", "eip", "rbp", "esp", "rsp", "rax", "eax"):
                ttype = Token.Generic.Heading
            else:
                ttype = Token.Comment

            print("%s%s" % (
                    Formattable(((ttype, "%-4s" % reg),
                                 (Token.Comment, ": "))),
                    memory.refchain(val)))
