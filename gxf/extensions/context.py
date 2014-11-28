# -*- coding: utf-8 -*-

import gxf
import gdb

@gxf.register()
class Context(gxf.DataCommand):
    '''
    Displays information about the current execution context.
    '''

    def setup(self, parser):
        parser.add_argument("-r", "--regs", action="store_true")
        parser.add_argument("-c", "--code", action="store_true")
        parser.add_argument("-s", "--stack", action="store_true")

    def run(self, args):

        def section(name):
            print(name.center(80, "-"))

        if not any((args.regs, args.code, args.stack)):
            args.regs = True
            args.code = True
            args.stack = True

        if args.regs:
            section("registers")
            print("   todo")

        if args.code:
            section("code")
            gxf.execute("gx heading $pc -b3 -c5", True, False)

        if args.stack:
            section("stack")
            gxf.execute("gx telescope $sp -c8", True, False)


