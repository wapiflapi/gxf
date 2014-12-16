# -*- coding: utf-8 -*-

import gxf


@gxf.register(prefix=True)
class Gx(gxf.Command):
    '''
    This is the important gx main command, it does nothing.

    This is used as a prefix command for all the extensions
    included with the gfx framework.
    '''

    def run(self, args):
        pass

# Extensions loaded when import gx:

with gxf.register.prefix("gx"):
    import gxf.extensions.reload        # NOQA
    import gxf.extensions.meta          # NOQA
    import gxf.extensions.testi         # NOQA
    import gxf.extensions.binexpect     # NOQA

    import gxf.extensions.telescope     # NOQA
    import gxf.extensions.addr          # NOQA
    import gxf.extensions.vmaps         # NOQA
    import gxf.extensions.disassemble   # NOQA
    import gxf.extensions.heading       # NOQA
    import gxf.extensions.pae           # NOQA
    import gxf.extensions.context       # NOQA
    import gxf.extensions.registers     # NOQA
    import gxf.extensions.cyclic        # NOQA
