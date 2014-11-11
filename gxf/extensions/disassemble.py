# -*- coding: utf-8 -*-

import sys

import gxf
import pygments

@gxf.register()
class Disassemble(gxf.DataCommand):
    '''
    Disassemble a specified section of memory.
    '''

    def setup(self, parser):
        parser.add_argument("what", type=gxf.LocationType())
        parser.add_argument("-c", "--count", type=int, default=5)
        parser.add_argument("-o", "--offset", type=int, default=0)
        parser.add_argument("-r", "--real", action="store_true")
        parser.add_argument("-v", "--verbose", action="store_true")

    def run(self, args):
        disassembly = gxf.disassembly.disassemble_lines(
            args.what, args.count, args.offset, ignfct=args.real)
        if args.verbose and disassembly.msg:
            print(disassembly.msg)
        disassembly.output()
