# -*- coding: utf-8 -*-

import collections
import gxf


def get_addrsz():
    return int(gxf.parse_and_eval("sizeof (void *)"))


class Registers(object):

    # ARM specific
    CPSR_V = 1 << 28
    CPSR_C = 1 << 29
    CPSR_Z = 1 << 30
    CPSR_N = 1 << 31

    # x86(_64) specific
    EFLAGS_CF = 1 << 0
    EFLAGS_PF = 1 << 2
    EFLAGS_AF = 1 << 4
    EFLAGS_ZF = 1 << 6
    EFLAGS_SF = 1 << 7
    EFLAGS_TF = 1 << 8
    EFLAGS_IF = 1 << 9
    EFLAGS_DF = 1 << 10
    EFLAGS_OF = 1 << 11

    impact = {
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

    def __init__(self):
        data = gxf.execute("info registers", False, True)

        self.regs = collections.OrderedDict()
        for l in data.splitlines():
            sl = l.split(None, 2)
            self.regs[sl[0]] = int(sl[1], 0)

        self.flags = {}

        if 'eflags' in self.regs: # x86
            eflags = self.regs["eflags"]

            self.flags["CF"] = bool(eflags & self.EFLAGS_CF)
            self.flags["PF"] = bool(eflags & self.EFLAGS_PF)
            self.flags["AF"] = bool(eflags & self.EFLAGS_AF)
            self.flags["ZF"] = bool(eflags & self.EFLAGS_ZF)
            self.flags["SF"] = bool(eflags & self.EFLAGS_SF)
            self.flags["TF"] = bool(eflags & self.EFLAGS_TF)
            self.flags["IF"] = bool(eflags & self.EFLAGS_IF)
            self.flags["DF"] = bool(eflags & self.EFLAGS_DF)
            self.flags["OF"] = bool(eflags & self.EFLAGS_OF)
        elif 'cpsr' in self.regs: # ARM
            cpsr = self.regs["cpsr"]

            self.flags["N"] = bool(cpsr & self.CPSR_N)
            self.flags["Z"] = bool(cpsr & self.CPSR_Z)
            self.flags["V"] = bool(cpsr & self.CPSR_V)
            self.flags["C"] = bool(cpsr & self.CPSR_C)
        

    def get(self, reg):
        """
        This does not always return the exact value of a register.
        For example .get('al') will return the value of rax.
        """

        while reg not in self.regs:
            reg = self.impact[reg][0]
        return self.regs[reg]
