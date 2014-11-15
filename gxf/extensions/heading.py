# -*- coding: utf-8 -*-

import gxf


@gxf.register()
class Heading(gxf.DataCommand):
    '''
    instruction trace thingy
    '''

    def setup(self, parser):
        parser.add_argument("what", type=gxf.LocationType())
        parser.add_argument("-b", "--before", type=int, default=0)

    def run(self, args):

        gxf.disassemble_heading(args.what, offset=-args.before)
