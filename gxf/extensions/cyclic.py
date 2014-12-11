# -*- coding: utf-8 -*-

import gxf

@gxf.register()
class cyclic(gxf.DataCommand):
    '''
    Manipulates De Bruijn sequences.
    '''

    def setup(self, parser):
        parser.add_argument("-a", "--alphabet", default=gxf.cyclic.dfltalphabet)
        parser.add_argument("-n", "--ordern", type=int, default=gxf.cyclic.dfltlength)
        parser.add_argument("length", nargs="?", type=int, default=256)

        parser.add_argument("-s", "--search", type=str, default=None)

    def run(self, args):

        db = gxf.cyclic.DeBruijn(a=args.alphabet.encode("utf8"), n=args.ordern)

        if args.search is not None:
            for offset in db.offsets(args.search.encode("utf8")):
                print(offset)
        else:
            print("".join("%c" % c for c in db[:args.length]))
