# -*- coding: utf-8 -*-

import struct

import gxf
import gdb

from pygments.token import Token


class RefChain(list, gxf.Formattable):
    def __init__(self, memory, addr):

        chain = []

        while True:

            if any(x[0] == addr for x in chain):
                val = ...
                break

            try:
                m = memory.get_map(addr)
                val = memory.read_ptr(addr)
            except gxf.MemoryError:
                break

            chain.append([addr, m, val])
            addr = val


        if not chain:
            # This wasn't even a valid pointer. We use the wanabee
            # address as value. (maybe taken from a register or other)
            chain.append([None, None, addr])

        # Now we examine the last element of the chain and we
        # try to find a better representation of its value.
        chain[-1][2] = self.guesstype(*chain[-1])

        self.chain = chain

        list.__init__(self, self.chain)
        gxf.Formattable.__init__(self)

    def guesstype(self, addr, m, val):

        # TODO: when memory will know about ELF or other formats
        # it will be possibile to have more info about code / rodata.
        # we'll need to take this into account here to.

        # TODO: We should take little/big endian into account
        # to do this properly.

        bval = struct.pack("q", int(val))

        # We only check utf8, do we need more?

        invalid = 8
        try:
            sval = bval.decode("utf8")
        except UnicodeDecodeError as e:
            invalid = e.start
            sval = bval[:invalid].decode("utf8")

        nullbyte = sval.find("\x00")
        if nullbyte >= 0:
            sval = sval[:nullbyte]

        if (len(sval) >= 3 and invalid != len(sval)) or len(sval) in (4, 8):
            return sval

        if "x" in m.perms:
            # Not a string and executable, this might be disassembly.
            disline = gxf.disassemble_lines(addr, ignfct=True).lines[0]
            if disline.inst is not None:
                return disline

        # Not a string, not disassembly, what else?
        return val

    def fmttokens(self):

        for addr, m, val in self[:-1]:
            yield from m.fmtaddr(addr)
            yield (Token.Comment, " : ")

        # The last element is special, we want to check if it can
        # format itself. We also have some special handling for
        # known types such as DisasselmblyLines.
        addr, mmap, val = self[-1]

        if isinstance(val, gxf.DisassemblyLine):
            # We format the address itself the way we do the others
            # but we let the instruction print the ':' because it
            # might want to print the function name before it.
            yield from mmap.fmtaddr(addr)
            yield (Token.Text, " ")
            yield from val.fmttokens(offset=val.addressidx+1,
                                     skipleading=True, style=None)

        elif isinstance(val, gxf.Formattable):
            yield from mmap.fmtaddr(addr)
            yield (Token.Comment, " : ")

            yield from val.fmttokens()

        elif isinstance(val, str):
            yield from mmap.fmtaddr(addr)
            yield (Token.Comment, " : ")
            yield (Token.Text, "%r" % val)

        else:
            yield from mmap.fmtaddr(addr)
            yield (Token.Comment, " : ")
            yield (Token.Text, ("%d" if abs(val) < 128 else "%#x") % int(val))




class MMap(gxf.Formattable):

    def __init__(self, start, end, perms, backing=None):
        if not backing:
            backing = None
        self.start = start
        self.end = end
        self.perms = perms
        self.backing = backing

    def __contains__(self, addr):
        return self.start <= addr < self.end

    def fmttokens(self):
        yield (Token.Text, "%#x-%#x %s %s\n" % (self.start, self.end, self.perms, self.backing))

    def fmtaddr(self, addr):

        if "x" in self.perms:
            token = Token.Generic.Deleted
        elif "w" in self.perms:
            token = Token.Keyword
        elif "r" in self.perms:
            token = Token.Generic.Inserted
        else:
            token = Token.Text

        yield (token, "%#.x" % addr)


class Memory(gxf.Formattable):

    def __init__(self):

        self.inf = gxf.inferiors.get_selected_inferior()

        if not self.inf.threads():
            raise ValueError("inferior is not running")

        self.maps = []

        # Ok if this fails:
        # either the process isn't running or you don't have access to its /proc/
        # if /proc/ isnt available please just `mount -t procfs proc /proc`
        # or implement something else in gxf.
        mapf = open("/proc/%d/maps" % self.inf.pid)

        for line in mapf:
            startend, perms, _ = line.split(None, 2)
            _, backing = line.rsplit(None, 1)

            start, end = (int(x, 16) for x in startend.split("-"))
            self.maps.append(MMap(start, end, perms, backing))

    def read_ptr(self, addr):
        # TODO: maybe use read_memory stuff ?
        return gxf.parse_and_eval("*(void **)%#x" % addr)

    def get_map(self, addr):
        for m in self.maps:
            if addr in m:
                return m
        raise gxf.MemoryError(addr)

    def refchain(self, addr):
        return RefChain(self, addr)

    def fmttokens(self):
        for mmap in self.maps:
            yield from mmap.fmttokens()
