# -*- coding: utf-8 -*-

import gxf


@gxf.register()
class Heading(gxf.DataCommand):
    '''
    instruction trace thingy
    '''

    def setup(self, parser):
        parser.add_argument("what", type=gxf.LocationType())
        parser.add_argument("-c", "--count", type=int, default=10)
        parser.add_argument("-b", "--before", type=int, default=0)

    def run(self, args):

        trunk, branch, future, stop = gxf.disassemble_heading(
            args.what, count=args.count + args.before, offset=-args.before)

        trunk.output(stop=branch)

        if future:
            print("future:")
            future.output(stop=stop)

            print("alternative:")
            trunk.output(start=branch)
