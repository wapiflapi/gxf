# -*- coding: utf-8 -*-

import sys

import gdb
import gxf

@gxf.register()
class Pae(gxf.UserCommand):
    '''
    Interface to gdb's parse_and_eval
    '''

    def setup(self, parser):
        parser.add_argument("what")
        parser.add_argument("-a", "--asm", action="store_true")

    def run(self, args):


        if not args.asm:
            try:
                print(gdb.parse_and_eval(args.what))
            except gxf.GdbError as e:
                exit(e)
            return



        fakei = "test %s" % args.what
        disass = gxf.disassembly.DisassemblyBlock(fakei)
        expression = disass.lines[0].get_expression()

        print(expression.format())

        try:
            print(expression.eval())
        except gxf.GdbError as e:
            exit(e)

