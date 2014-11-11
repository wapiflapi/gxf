# -*- coding: utf-8 -*-

import gxf


@gxf.register()
class TestI(gxf.MaintenanceCommand):
    '''
    This tests stuff related to inferiors.
    '''

    def setup(self, parser):
        self.setup_inferior(parser)

    def run(self, args):
        print(args)
