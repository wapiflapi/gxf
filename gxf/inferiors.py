# -*- coding: utf-8 -*-

import gdb


def get_inferiors():
    yield from gdb.inferiors()


def get_inferior_by_id(iid):
    for inferior in get_inferiors():
        if inferior.num == iid:
            return inferior
    raise KeyError("No such inferior %s." % iid)


def get_selected_inferior():
    return gdb.selected_inferior()
