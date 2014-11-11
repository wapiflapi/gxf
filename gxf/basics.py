# -*- coding: utf-8 -*-

import gdb
import gxf

def execute(*args, **kwargs):

    try:
        return gdb.execute(*args, **kwargs)
    except gdb.MemoryError as e:
        raise gxf.MemoryError(e)
