# -*- coding: utf-8 -*-

import math

import gxf
import gdb

@gxf.register()
class Telescope(gxf.DataCommand):
    '''
    Shows memory.
    '''

    def setup(self, parser):
        parser.add_argument("what", type=gxf.LocationType())
        parser.add_argument("until", type=gxf.LocationType(), nargs='?')
        parser.add_argument("-c", "--count", type=int, default=10)
        parser.add_argument("-b", "--before", type=int, default=0)
        parser.add_argument("-s", "--size", type=int, default=None)

    def run(self, args):

        size = int(args.size or gxf.cpu.get_addrsz())
        start = int(args.what - args.before * size)
        end = int(args.until or args.what + args.count * size)

        m = max(abs(start - int(args.what)), abs(end - int(args.what) - 1))

        ow = math.floor(math.log(m, 10)) + 1
        iw = math.floor(math.log(m / size, 10)) + 1
        aw = math.floor(math.log(end, 10)) + 1

        memory = gxf.Memory()

        for addr in range(start, end, size):
            offset = addr - int(args.what)
            refchain = memory.refchain(addr)

            print("   %*.d/%-*.d " % (ow, offset, iw, abs(offset//size)), end="")
            refchain.output()
