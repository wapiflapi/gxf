#!/usr/bin/env python

import gc

import tabulate

import gxf


@gxf.register()
class Meta(gxf.MaintenanceCommand):
    '''
    This command shows debuging information about gxf itself.
    '''

    def setup(self, parser):
        pass

    def run(self, args):

        print("Gxf %s - %s\n" % (gxf.__version__, gxf.__author__))

        gcstats = gc.get_stats()

        headers = ["generation", "collections", "collected", "uncollectable"]
        tbldata = [["gen %d" % i] + [s[h] for h in headers[1:]]
                   for i, s in enumerate(gcstats)]

        print("Garbage collector statistics:\n")
        print(tabulate.tabulate(tbldata, headers=headers))
