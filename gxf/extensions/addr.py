# -*- coding: utf-8 -*-

import gxf
import gdb

@gxf.register()
class Addr(gxf.DataCommand):
    '''
    Show info about an address.
    '''

    def setup(self, parser):
        parser.add_argument("what", type=gxf.LocationType())

    def run(self, args):

        memory = gxf.Memory()

        refchain = memory.refchain(args.what)

        refchain.output()
        mmap = refchain[0][1]
        mmap.output()
