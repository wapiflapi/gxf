# -*- coding: utf-8 -*-

import collections
import gxf


def get_addrsz():
    return int(gxf.parse_and_eval("sizeof (void *)"))


class Registers(object):

    EFLAGS_CF = 1 << 0
    EFLAGS_PF = 1 << 2
    EFLAGS_AF = 1 << 4
    EFLAGS_ZF = 1 << 6
    EFLAGS_SF = 1 << 7
    EFLAGS_TF = 1 << 8
    EFLAGS_IF = 1 << 9
    EFLAGS_DF = 1 << 10
    EFLAGS_OF = 1 << 11

    def __init__(self):
        data = gxf.execute("info registers", False, True)

        self.regs = collections.OrderedDict()
        for l in data.splitlines():
            sl = l.split(None, 2)
            self.regs[sl[0]] = int(sl[1], 0)

        eflags = self.regs["eflags"]

        self.flags = {}

        self.flags["CF"] = bool(eflags & self.EFLAGS_CF)
        self.flags["PF"] = bool(eflags & self.EFLAGS_PF)
        self.flags["AF"] = bool(eflags & self.EFLAGS_AF)
        self.flags["ZF"] = bool(eflags & self.EFLAGS_ZF)
        self.flags["SF"] = bool(eflags & self.EFLAGS_SF)
        self.flags["TF"] = bool(eflags & self.EFLAGS_TF)
        self.flags["IF"] = bool(eflags & self.EFLAGS_IF)
        self.flags["DF"] = bool(eflags & self.EFLAGS_DF)
        self.flags["OF"] = bool(eflags & self.EFLAGS_OF)
