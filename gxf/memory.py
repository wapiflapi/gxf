# -*- coding: utf-8 -*-

import gxf
import gdb

from pygments.token import Token


class RefChain(list, gxf.Formattable):
    def __init__(self, memory, addr):

        chain = []

        while True:

            if any(x[0] == addr for x in chain):
                chain[-1][2] = ...
                break

            try:
                m = memory.get_map(addr)
            except gxf.MemoryError:

                if not chain:
                    # This means the first address failed.
                    raise

                chain[-1][2] = addr
                break


            val = memory.read_ptr(addr)
            chain.append([addr, m, val])


            if "x" in m.perms:
                chain[-1][2] = gxf.disassemble_lines(addr, ignfct=True).lines[0]
                break

            addr = val


        # TODO:
        # We should check if the value of the last element in chain
        # is something we can guess. In particular this is where we
        # should retrieve a larger portion of the string if those
        # bytes are printable. We smart about heuristics. Peda messes
        # up from time to time, try to do things better.

        self.chain = chain

        list.__init__(self, self.chain)
        gxf.Formattable.__init__(self)


    def fmttokens(self):

        for addr, mmap, val in self[:-1]:
            yield from mmap.fmtaddr(addr)
            yield (Token.Text, " : ")


        # For the last element its special, if formatable we
        # dont want to print the address ? (its probably disass)
        addr, mmap, val = self[-1]

        if isinstance(val, gxf.Formattable):

            # TODO: there is a problem with showing disass like this
            # the lines start with spaces to leave place for the
            # occasional "=>", what should we do about this?

            yield from val.fmttokens()
        else:
            yield from mmap.fmtaddr(addr)
            yield (Token.Text, " : ")

            if isinstance(val, str):
                yield (Token.Text, "%s" % val)
            else:
                yield (Token.Text, "%#x" % int(val))




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
