# -*- coding: utf-8 -*-

import sys
import importlib

import gxf


@gxf.register()
class Reload(gxf.MaintenanceCommand):
    '''
    This command can be used to reload packages from source.
    '''

    def setup(self, parser):
        parser.add_argument(
            'package', nargs='*', default=['gxf', 'gxf.extensions'],
            help='packages to be reloaded, '
            'defaults to gxf and gxf.extensions.')

    def run(self, args):
        toreload, toremove = set(), set()
        packages = [(p, p.split('.')) for p in args.package]
        for name, module in sys.modules.items():
            path = name.split('.')
            for p, ps in packages:
                if p == name:
                    toreload.add(name)
                elif ps == path[:len(ps)]:
                    toremove.add(name)

        for name in toremove:
            if name not in toreload:
                del sys.modules[name]

        for name in sorted(toreload):
            importlib.reload(sys.modules[name])

