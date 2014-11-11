# -*- coding: utf-8 -*-

import pygments
from pygments.lexers import NasmLexer, GasLexer
from pygments.lexers import CppObjdumpLexer, NasmObjdumpLexer
from pygments.formatters import TerminalFormatter
from pygments.filter import Filter
from pygments.lexer import DelegatingLexer, RegexLexer, inherit, bygroups
from pygments.token import *

import re
import gdb
import gxf

from contextlib import contextmanager

class DisassemblyFlavour(gdb.Parameter):

    def __init__(self):
        self.message = gdb.execute("show disassembly-flavor", False, True).strip()
        value = gdb.parameter("disassembly-flavor")
        super().__init__("disassembly-flavor", gdb.COMMAND_DATA, gdb.PARAM_ENUM, [value])
        self.value = value

    def get_set_string(self):
        return self.message

    def get_show_string(self, svalue):
        return self.message

disassemblyflavour = DisassemblyFlavour()


class GdbContextLexer(RegexLexer):

    tokens = {
        'root': [
            ('[ \t]+', Text),
            (r'=>', Comment),
            (r'0x[0-9a-f]+', Comment, 'gx_location'),
            (r'[0-9a-f]{2}[ \t]', Comment.Special),
            ('\(bad\)', Comment),
            ('.*\n', Other),
            ],
        'gx_location': [
            ('[ \t]+', Text),
            (':', Comment, '#pop'),
            ('(<)(.*)(\+)([0-9]+)(>)(:)', bygroups(
                    Operator,
                    Name.Variable, Operator, Literal.Number.Integer,
                    Operator, Comment), '#pop'),
            ]
        }


class GdbLexer(DelegatingLexer):

    rootlexers = {
        'intel': NasmLexer,
        'att': GasLexer
        }

    def __init__(self):
        super().__init__(self.rootlexers[disassemblyflavour.value], GdbContextLexer)

    EXTRA_KEYWORDS = set(["PTR", "data16", "WORD", "HWORD", "DWORD", "QWORD", "XMMWORD"])

    EXTRA_BUILTINS = set(["r%d" % i for i in range(16)] +
                         ["xmm%d" % i for i in range(16)])

    # TODO:
    # Fix data16, rex.RB, stuff like that.
    # also in att: and (?!)

    def get_tokens_unprocessed(self, text):
        for index, token, value in super().get_tokens_unprocessed(text):
            if token is Name.Variable and value in self.EXTRA_BUILTINS:
                yield index, Name.Builtin, value
            elif token is Name.Variable and value in self.EXTRA_KEYWORDS:
                yield index, Keyword.Type, value
            else:
                yield index, token, value


class CurrentFunctiontFilter(Filter):

    def __init__(self, *args, **kwargs):
        self._current_function = ''

    @contextmanager
    def current_function(self, fct):
        self._current_function = fct
        yield
        self._current_function = ''

    def filter(self, lexer, stream):
        maybe = False
        for ttype, value in stream:
            if maybe:
                maybe = False
                if ttype is Operator and value == "+":
                    yield Name.Variable, self._current_function
            elif ttype is Operator and value == "<":
                maybe = True
            yield ttype, value

class AlignementFilter(Filter):

    def filter(self, lexer, stream):

        lexed = list(map(list, stream))

        hexdumps = {}
        count = 0
        for i, token in enumerate(lexed):
            if token[0] is Comment.Special:
                token[1] = token[1].strip() + ' '
                count += 1
            elif count > 0:
                hexdumps[i-count] = count
                count = 0

        if hexdumps:

            # This is not a real median, its 90%.
            median = sorted(hexdumps.values())[int(len(hexdumps)*0.9)]

            for i, count in hexdumps.items():
                token = lexed[i + count - 1]
                value = token[1]

                backoff = 2
                padding = median
                while padding < count:
                    padding += backoff
                    backoff *= 2

                padding = int(padding) - count
                value += padding * 3 * ' '

                token[1] += value

        yield from lexed


class ControlFlowFilter(Filter):

    phonycomments = (Comment, Keyword, Generic.Error,
                     Generic.Inserted, Generic.Strong)

    def filter(self, lexer, stream):

        line = []
        function = None
        for ttype, value in stream:

            entry = [ttype, value]
            line.append(entry)

            if function is None and ttype is Name.Function:
                function = entry
            if not "\n" in value:
                continue

            marking = Comment
            if function is None:
                pass # weird.
            elif function[1].startswith("j"):
                function[0] = marking = Keyword
            elif function[1] == "syscall":
                function[0] = marking = Generic.Error
            elif "ret" in function[1]:
                function[0] = marking = Generic.Error
            elif "call" in function[1]:
                function[0] = marking = Generic.Inserted
            elif "cmp" in function[1] or "test" in function[1]:
                marking = Generic.Strong


            for entry in line:
                # If bytecode should be an indicator of the instruction
                # type we should add Commebt.Special in the following:
                if entry[0] in (Comment, ):
                    entry[0] = marking

            yield from line
            function = None
            line = []

currentfunctiontfilter = CurrentFunctiontFilter()
lexer = GdbLexer()
lexer.add_filter(currentfunctiontfilter)
lexer.add_filter(AlignementFilter())
lexer.add_filter(ControlFlowFilter())

formatter = TerminalFormatter(bg="dark")


class Disassembly(object):

    def __init__(self, disassembly, lexer=lexer, msg=None):

        if not disassembly:
            self.lexed = []
        elif isinstance(disassembly, list):
            self.lexed = disassembly
        elif disassembly:
            current_function = msg.rsplit(None, 1)[-1][:-1]
            with currentfunctiontfilter.current_function(current_function):
                self.lexed = list(pygments.lex(disassembly, lexer))

        self.msg = msg
        self._lines = None

    @property
    def lines(self):
        if self._lines is not None:
            return self._lines

        lines = []

        count = 0
        address = None

        for i, token in enumerate(self.lexed):
            count += 1

            if address is None and token[0] in ControlFlowFilter.phonycomments:
                try:
                    address = int(token[1], 0)
                except ValueError:
                    pass
            if "\n" in token[1]:
                if address is None:
                    # print(len(self.lexed), i, count, self.lexed[i-count+1:i+1])
                    raise RuntimeError("Assembly line without address.")
                lines.append((i-count+1, count, address))
                count = 0
                address = None

        self._lines = lines
        return self._lines

    def get_addr_for_line(self, line):
        return self.lines[line][2]

    def get_line_for_addr(self, addr):
        best = None
        for i, line in enumerate(self.lines):
            if line[2] > addr:
                break
            best = i

        return best

    def format(self, formatter=formatter):
        return pygments.format(self.lexed, formatter)

    def output(self):
        print(self.format(), end="")

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, key):
        copy = Disassembly(self.lexed, msg=self.msg)
        copy.truncate(key)
        return copy

    def truncate(self, key, *args):
        if not isinstance(key, slice):
            key = slice(max(key, 0), *args)

        lines = self.lines[key]
        if lines:
            self.lexed = self.lexed[lines[0][0]:lines[-1][0]+lines[-1][1]]
        else:
            self.lexed = []

        self._lines = None
        return self


    def __truncate_addr(self, startline=None, endline=None, startaddr=None, endaddr=None):

        # untested.

        startl, endl = startline, endline
        for i in range(len(self)):
            lineaddr = self.get_lineaddr(i)

            if (startaddr and lineaddr > startaddr) and (endaddr and lineaddr >= endaddr):
                break

            if startline is None and startaddr is not None and lineaddr <= startaddr:
                startl = i
            if endline is None and endaddr is not None and lineaddr < endaddr:
                endl = i

        return self.truncate(startl, endl)


# disassemble is a direct wrapper for gdb's disassemble.

def _disassemble(startaddr, endaddr=None, hexdump=False, ignmemerr=False):
    modifier = " /r" if hexdump else ""
    what = ",".join(str(int(addr)) for addr in (startaddr, endaddr) if addr)
    try:
        data = gxf.execute("disassemble%s %s" % (modifier, what), False, True)
    except gxf.MemoryError as e:
        if not ignmemerr:
            raise
        # if failaddr == startaddr this will return nothing.
        return disassemble(startaddr, e.address, hexdump)

    start, end = data.find('\n')+1, data.rfind('\n', 0, -1)
    return data[start:end], data[:start-1]

def disassemble(startaddr, endaddr=None, hexdump=False, ignmemerr=False):
    data, msg = _disassemble(startaddr, endaddr, hexdump, ignmemerr)
    return Disassembly(data, msg=msg)


def _check_data(data, addr):
    lastbad = True
    for i, line in enumerate(data.splitlines()):
        if "(bad)" in line:
            lastbad = i

        # Get this line's address:
        a, line = line.split(None, 1)
        if a == "=>":
            a, line = line.split(None, 1)
        a = int(a.rstrip(':'), 0)

        if a == addr:
            return lastbad
        if a > addr:
            break

    return None


def disassemble_lines(addr, count=1, offset=0, hexdump=False, ignfct=False):
    addr = int(addr)

    if ignfct is False:

        try:
            disfct = disassemble(addr, hexdump=hexdump)
            line = disfct.get_line_for_addr(addr)
            assert line is not None, "addr should be in function."
            # If offset is outside of function we don't to fallback.
            # If the user wanted that he should have:
            #   - used ignfct if he wanted an exact match (if possible).
            #   - passed addr=addr+offset if he wanted results
            #     always including addr. .
            return disfct.truncate(line+offset, line+offset+count)
        except gxf.MemoryError:
            raise # Nothing we can do about this.
        except gdb.error:
            # This probably means the address is not in a function
            # we need to fallback on the harder method.
            pass

    if offset >= 0:
        # plain old linear sweep.
        disafter = disassemble(addr, addr + offset*16 + count*16,
                               hexdump=hexdump, ignmemerr=True)
        return disafter[offset:offset+count]


    # Now we need to use backwards disassembling hacks :-)

    hexaddr = "%x" % addr # This has false positives, its not a problem.

    backguess = addr + offset*16 - 64 # 64 gives it time to automagically sync.

    dbg_cnt = 0

    badblocks = []

    baddr, bdata, bmsg = None, None, None

    for backguess in range(backguess, backguess+16):
        data, msg = _disassemble(backguess, backguess + count*16, ignmemerr=False)
        dbg_cnt += 1

        if hexaddr in data:
            check = _check_data(data, addr)
            if check is True:
                break
            if check is not None and check < baddr:
                baddr, bdata, bmsg = check, data, msg

    else:

        # no dice, lets check if we have some matching targets that
        # simply have some (bad)s. We'll take the furthest away.

        if bdata is not None:
            data, msg = bdata, bmsg

        else:
            # This stream is target address is probably fucked up, otherwise
            # we would have synced already. Lets try this from the target,
            # then we'll know soon if it is even possible to get there.

            check = None
            bads = 0

            print(hex(addr), hex(addr + offset*16 - 1), hex(-1))
            # We start at addr, that should give us at least one good one.
            for backguess in range(addr, addr + offset*16 - 1, -1):
                bdata, bmsg = _disassemble(backguess, backguess + count*16, ignmemerr=False)
                dbg_cnt += 1

                if hexaddr in bdata and _check_data(bdata, addr) is not None:
                    # New best thing?
                    data, msg = bdata, bmsg
                    bads = 0
                elif bads == 15:
                    # We will never hit it again.
                    break
                else:
                    bads += 1


    print("%d sync tries." % dbg_cnt)
    disassembly = Disassembly(data, msg=msg)
    line = disassembly.get_line_for_addr(addr)
    print(len(disassembly), line, offset, count)
    assert line is not None, "addr should be in function."
    return disassembly.truncate(line+offset, line+offset+count)

    return

# Ideas for names for the next function:
# live
# real time , rt
# context
#
