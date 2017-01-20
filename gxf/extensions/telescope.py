# -*- coding: utf-8 -*-

import gxf


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

        size = args.size or gxf.cpu.get_addrsz()
        start = args.what - args.before * size
        end = args.until or args.what + args.count * size

        memory = gxf.Memory()

        # FIXME: WTF. need to find a gdb solution or a gxf hack.
        def posint(x): return int(x) & 0xffffffffffffffff
        for addr in range(posint(start), posint(end), posint(size)):
            offset = addr - posint(args.what)
            refchain = memory.refchain(addr)

            print("%2.d " % (offset, ), end="")
            refchain.output()
