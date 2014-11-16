# -*- coding: utf-8 -*-

import gxf


@gxf.register()
class Disassemble(gxf.DataCommand):
    '''
    Disassemble a specified section of memory.
    '''

    def setup(self, parser):
        parser.add_argument("what", type=gxf.LocationType())
        parser.add_argument("until", type=gxf.LocationType(), nargs='?')
        parser.add_argument("-v", "--verbose", action="store_true")

        parser.add_argument("-f", "--function", action="store_true")
        parser.add_argument("-c", "--count", type=int, default=10)
        parser.add_argument("-b", "--before", type=int, default=0)
        parser.add_argument("-r", "--real", action="store_true")
        parser.add_argument("-x", "--hexdump", action="store_true")

    def run(self, args):

        if args.function:
            try:
                disassembly = gxf.disassembly.disassemble(args.what, None)
            except gxf.GdbError as e:
                exit(e)
        elif args.until is not None:
            disassembly = gxf.disassembly.disassemble(args.what, args.until)
        else:
            disassembly = gxf.disassembly.disassemble_lines(
                args.what, args.count + args.before, -args.before,
                ignfct=args.real)

        if args.verbose and disassembly.msg:
            print(disassembly.msg)
        elif not args.function:
            print("   ...")

        disassembly.output(hexdump=args.hexdump)

        if not args.function:
            print("   ...")
