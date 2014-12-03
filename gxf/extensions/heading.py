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

        try:
            trunk, branch, future, stop = gxf.disassemble_heading(
                args.what, count=args.count + args.before, offset=-args.before)
        except gxf.MemoryError as e:
            if e.address == args.what:
                print("Invalid address %#x." % e.address)
                return
            else:
                # This is probably a bug :S
                raise

        trunk.output(stop=branch)

        if future:
            print("future:")
            future.output(stop=stop)

            print("alternative:")
            trunk.output(start=branch)
