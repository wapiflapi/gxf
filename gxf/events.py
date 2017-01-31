# -*- coding: utf-8 -*-

import traceback

import gdb
import gxf


cont = gdb.events.cont
stop = gdb.events.stop
exited = gdb.events.exited
new_objfile = gdb.events.new_objfile


class HookEvent(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.value = None


class HookEventRegistry(object):

    def __init__(self):
        self.handlers = []

    def connect(self, handler):
        self.handlers.append(handler)

    def disconnect(self, handler):
        self.handlers.remove(handler)

    def __call__(self, *args, **kwargs):

        event = HookEvent(*args, **kwargs)

        for handler in self.handlers:
            value = handler(event)
            if value is not None:
                event.value = value

        return event.value


prompt = HookEventRegistry()
gdb.prompt_hook = prompt


class Handler(object):

    class Checker(object):

        def __init__(self, registry):
            self.activated = False
            registry.connect(self)

        def __call__(self, *args, **kwargs):
            self.activated = True

        def reset(self):
            activated = self.activated
            self.activated = False
            return activated

    def __init__(self, onlyafter=(), notafter=()):

        self.must = [self.Checker(r) for r in onlyafter]
        self.cant = [self.Checker(r) for r in notafter]

    def __call__(self, *args, **kwargs):

        go = True

        for c in self.must:
            if c.reset() is False:
                go = False

        for c in self.cant:
            if c.reset() is True:
                go = False

        try:
            if go is False:
                return self.bail(*args, **kwargs)
            else:
                return self.handle(*args, **kwargs)
        except BaseException:
            print("%s" % (traceback.format_exc(),), end="")

    def bail(self, *args, **kwargs):
        return None


class ExecutingHandler(Handler):

    def __init__(self, cmds, *args, **kwargs):
        self.cmds = (cmds,) if isinstance(cmds, str) else cmds
        super().__init__(*args, **kwargs)

    def handle(self, *args, **kwargs):
        for cmd in self.cmds:
            gxf.execute(cmd, tty=True, tostr=False)

prompt.connect(ExecutingHandler("gx context", onlyafter=(stop,)))
