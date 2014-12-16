# -*- coding: utf-8 -*-

import os
import sys
import shlex
import subprocess
import argparse

import gxf


# This function is stolen from binexpect.
def spawn_terminal(terminal, *cmdline):
    '''
    There doesn't seem to be a portable way of starting a terminal.
    This works for me =)
    '''

    cmd = shlex.split(terminal)
    if len(cmd) == 1:
        cmd.append("-e")
    cmd.extend(cmdline)

    subprocess.Popen(cmd, stdin=None, stdout=None, stderr=None,
                     close_fds=True, shell=False)


@gxf.register()
class Binexpect(gxf.UserCommand):
    '''
    This command is used to interface gxf and binexpect.
    '''

    def setup(self, parser):
        parser.add_argument("exploit", type=gxf.FilePathType(),
                            help="the exploit to start")

        parser.add_argument("--terminal", default=os.getenv("TERMINAL", "x-terminal-emulator"),
                            help="specify the terminal to use, by default -e will be used "
                            "to pass the arguments but if options are already present it "
                            "will not be added.")

        parser.add_argument("-w", "--wait", action="store_true",
                            help="Do not re-run the program imediatly, "
                            "this is useful if you want to pass arguments.")

        parser.add_argument("args", nargs=argparse.REMAINDER,
                            help="the exploit's arguments")


    def run(self, args):

        fifo = "/tmp/gxf"

        try:
            os.unlink(fifo)
        except:
            pass

        os.mkfifo(fifo)

        spawn_terminal(args.terminal, args.exploit, "--tty", "--writeback", fifo, *args.args)

        while True:
            try:
                # TODO add alarm, gdb isnt catching ctrl-c if no interupts occur.
                back = open(fifo)
            except InterruptedError:
                continue
            else:
                break

        data = ""
        while True:
            arg = back.read()
            if arg:
                data += arg
            else:
                break

        os.unlink(fifo)

        targetargs = data.split("\x00")
        tty, targetargs = targetargs[0], targetargs[1:]

        print("binexpect started tty at %s" % tty)
        print("binexpect recommends run %s" % " ".join(targetargs))

        gxf.execute("set inferior-tty %s" % tty)

        if not args.wait:
            gxf.execute("run %s" % " ".join(targetargs))
