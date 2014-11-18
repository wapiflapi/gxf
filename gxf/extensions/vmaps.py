# -*- coding: utf-8 -*-

import gxf
import gdb

@gxf.register()
class Vmaps(gxf.DataCommand):
    '''
    Shows virtual memory mappings.
    '''

    def setup(self, parser):
        pass

    def run(self, args):

        memory = gxf.Memory()

        memory.output()
