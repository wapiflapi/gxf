# -*- coding: utf-8 -*-

import gxf

from gxf.formatting import Token, Formattable


@gxf.register()
class Registers(gxf.DataCommand):
    '''
    Shows registers.
    '''

    register_map = {
        "al": ("ax", "eax", "rax"), "ah": ("ax", "eax", "rax"),
        "bl": ("bx", "ebx", "rbx"), "bh": ("bx", "ebx", "rbx"),
        "cl": ("cx", "ecx", "rcx"), "ch": ("cx", "ecx", "rcx"),
        "dl": ("dx", "edx", "rdx"), "dh": ("dx", "edx", "rdx"),
        "ax": ("eax", "rax"),
        "bx": ("ebx", "rbx"),
        "cx": ("ecx", "rcx"),
        "dx": ("edx", "rdx"),
        "eax": ("rax",),
        "ebx": ("rbx",),
        "ecx": ("rcx",),
        "edx": ("rdx",),
        "esi": ("rsi",),
        "edi": ("rdi",),
        "ebp": ("rbp",),
        "esp": ("rdp",),
        "eip": ("rip",),
        "pc": ("eip", "rip"),
        }

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
            dis = gxf.disassemble_lines(gxf.parse_and_eval("$pc")).lines[0]
            for _, t in dis.tokens[dis.instidx:]:
                tomark.append(t)
                tomark.extend(self.register_map.get(t, ()))

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
