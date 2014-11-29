# -*- coding: utf-8 -*-

import pygments
from pygments.lexers import NasmLexer, GasLexer
from pygments.lexers import CppObjdumpLexer, NasmObjdumpLexer
from pygments.filter import Filter
from pygments.lexer import DelegatingLexer, RegexLexer, inherit, bygroups
from pygments.token import Token

import re
import gdb
import gxf

from contextlib import contextmanager


def check_flags(inst):

    flags = gxf.Registers().flags

    if inst == "jmp":
        return True
    if inst == "je" and flags["ZF"]:
        return True
    if inst == "jne" and not flags["ZF"]:
        return True
    if inst == "jg" and not flags["ZF"] and (flags["SF"] == flags["OF"]):
        return True
    if inst == "jge" and (flags["SF"] == flags["OF"]):
        return True
    if inst == "ja" and not flags["CF"] and not flags["ZF"]:
        return True
    if inst == "jae" and not flags["CF"]:
        return True
    if inst == "jl" and (flags["SF"] != flags["OF"]):
        return True
    if inst == "jle" and (flags["ZF"] or (flags["SF"] != flags["OF"])):
        return True
    if inst == "jb" and flags["CF"]:
        return True
    if inst == "jbe" and (flags["CF"] or flags["ZF"]):
        return True
    if inst == "jo" and flags["OF"]:
        return True
    if inst == "jno" and not flags["OF"]:
        return True
    if inst == "jz" and flags["ZF"]:
        return True
    if inst == "jnz" and flags["OF"]:
        return True


class DisassemblyFlavor(gdb.Parameter):

    def __init__(self):
        self.message = gxf.execute("show disassembly-flavor").strip()
        value = gdb.parameter("disassembly-flavor")
        super().__init__(
            "disassembly-flavor", gdb.COMMAND_DATA, gdb.PARAM_ENUM, [value])
        self.value = value

    def get_set_string(self):
        return self.message

    def get_show_string(self, svalue):
        return self.message

disassemblyflavor = DisassemblyFlavor()


class GdbContextLexer(RegexLexer):

    tokens = {
        'root': [
            ('[ \t]+', Token.Text),
            (r'=>', Token.Comment),
            (r'0x[0-9a-f]+', Token.Comment, 'gx_location'),
            (r'[0-9a-f]{2}[ \t]', Token.Comment.Special),
            ('\(bad\)', Token.Comment),
            ('(.*?)(#.*)?(\n)', bygroups(
                    Token.Other, Token.Comment, Token.Other)),
            ],
        'gx_location': [
            ('[ \t]+', Token.Text),
            (':', Token.Comment, '#pop'),
            ('(<)(.*)(\+)([0-9]+)(>)(:)', bygroups(
                    Token.Operator, Token.Name.Variable, Token.Operator,
                    Token.Literal.Number.Integer,
                    Token.Operator, Token.Comment), '#pop'),
            ]
        }


class GdbLexer(DelegatingLexer):

    rootlexers = {
        'intel': NasmLexer,
        'att': GasLexer
        }

    def __init__(self):
        super().__init__(
            self.rootlexers[disassemblyflavor.value], GdbContextLexer)

    EXTRA_KEYWORDS = set(["PTR", "WORD", "HWORD", "DWORD",
                          "FWORD", "QWORD", "XMMWORD"])

    EXTRA_BUILTINS = set(["r%d" % i for i in range(16)] +
                         ["xmm%d" % i for i in range(16)])

    def get_tokens_unprocessed(self, text):
        for index, token, value in super().get_tokens_unprocessed(text):
            if token is Token.Name.Variable and value in self.EXTRA_BUILTINS:
                yield index, Token.Name.Builtin, value
            elif token is Token.Name.Variable and value in self.EXTRA_KEYWORDS:
                yield index, Token.Keyword.Type, value
            elif token is Token.Punctuation:
                for c in value:
                    if c in "+-*/%^&":
                        yield index, Token.Operator, c
                    else:
                        yield index, token, c
                    index += 1
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
                if ttype is Token.Operator and value == "+":
                    yield Token.Name.Variable, self._current_function
            elif ttype is Token.Operator and value == "<":
                maybe = True
            yield ttype, value


class PrefixFilter(Filter):

    prefixes = set(("ES", "CS", "NTAKEN", "SS", "DS", "TAKEN",
                    "REX", "REX.B", "REX.X", "REX.XB", "REX.R", "REX.RB",
                    "REX.RX", "REX.RXB", "REX.W", "REX.WB", "REX.WX",
                    "REX.WXB", "REX.WR", "REX.WRB", "REX.WRX", "REX.WRXB",
                    "FS", "ALTER", "GS", "LOCK",
                    "REPNZ", "REP",
                    "data16", "addr16", "data32", "addr32"))

    def filter(self, lexer, stream):

        prefix = False
        for ttype, value in stream:

            if prefix and ttype is Token.Name.Variable:
                if value in self.prefixes:
                    ttype = Token.Keyword.Type
                else:
                    ttype = Token.Name.Function

            elif ttype is Token.Name.Function and value in self.prefixes:
                prefix = True
                ttype = Token.Keyword.Type

            elif ttype is not Token.Text:
                prefix = False

            yield ttype, value


class AlignementFilter(Filter):

    def filter(self, lexer, stream):

        lexed = list(map(list, stream))

        hexdumps = {}
        count = 0
        for i, token in enumerate(lexed):
            if token[0] is Token.Comment.Special:
                token[1] = token[1].strip() + ' '
                count += 1
            elif count > 0:
                hexdumps[i - count] = count
                count = 0

        if hexdumps:

            # This is not a real median, its 90%.
            median = sorted(hexdumps.values())[int(len(hexdumps) * 0.9)]

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


currentfunctiontfilter = CurrentFunctiontFilter()
lexer = GdbLexer()
lexer.add_filter(PrefixFilter())
lexer.add_filter(currentfunctiontfilter)
lexer.add_filter(AlignementFilter())

JMP = "jmp"
CALL = "call"
SYSCALL = "syscall"
RET = "ret"
TEST = "test"


class DisassemblyLine(gxf.Formattable):

    formatting = {
        JMP: Token.Keyword,
        CALL: Token.Generic.Inserted,
        SYSCALL: Token.Generic.Inserted,
        RET: Token.Generic.Error,
        TEST: Token.Generic.Strong,
        }

    def __init__(self, tokens):
        self.tokens = tokens
        self.address = None
        self.addressidx = None
        self.inst = None
        self.instidx = None

        self.bytecode = []

        self.current = False

        next_is_function = False
        for i, (ttype, value) in enumerate(tokens):
            if ttype is Token.Comment and self.address is None:
                if value == "=>":
                    self.current = True
                else:
                    self.address = int(value, 0)
                    self.addressidx = i

            if ttype is Token.Comment.Special:
                self.bytecode.extend(int(v, 16) for v in value.split())

            if ttype is Token.Name.Function:

                self.inst = value
                self.instidx = i

        self.bytecode = bytes(self.bytecode)

        if self.inst is None:
            self.itype = None
        elif self.inst.startswith("j"):
            self.itype = JMP
        elif self.inst.startswith("call"):
            self.itype = CALL
        elif self.inst.startswith("syscall"):
            self.itype = SYSCALL
        elif "ret" in self.inst:
            self.itype = RET
        elif "cmp" in self.inst or self.inst == "test":
            self.itype = TEST
        else:
            self.itype = None

    def fmttokens(self, hexdump=False, offset=0, skipleading=False, style=True):

        # TODO: We need a way to remove indentation.
        # Something like skip spaces if more than one should do
        # the trick. It might be worth checking if this is doable
        # at the Formatable level ?

        if style is True:
            gstyle = Token.Generic.Heading if self.current else None
            style = self.formatting.get(self.itype)
        else:
            gstyle = style

        for ttype, value in self.tokens[offset:]:

            if skipleading and value.isspace():
                continue
            skipleading = False

            if not hexdump and ttype is Token.Comment.Special:
                continue

            # If bytecode should be an indicator of the instruction
            # type we should add Comment.Special in the following:
            if style and ttype in (Token.Comment, ):
                ttype = style
            if gstyle:
                ttype = gstyle
            yield ttype, value

    def fmtinsttokens(self, hexdump=False):
        if self.instidx is not None:
            yield from self.fmttokens(hexdump=hexdump, offset=self.instidx)
        else:
            yield (Token.Comment, "(bad)")

    def _convert_intel(self, tokens):

        relative = False
        ctokens = []

        for t, v in tokens:

            if v == "[":

                ctokens.append((Token.Operator, "*"))
                ctokens.append((Token.Punctuation, "("))

                # should convert types to cast here.
                ctokens.append((Token.Keyword.Type, "void"))
                ctokens.append((Token.Operator, "*"))

                ctokens.append((Token.Operator, "*"))
                ctokens.append((Token.Punctuation, ")"))
                ctokens.append((Token.Punctuation, "("))

            elif v == "]":
                ctokens.append((Token.Punctuation, ")"))

            elif t in (Token.Name.Variable, Token.Name.Builtin):
                if v in ("eip", "rip", "pc"):
                    ctokens.append((Token.Punctuation, "("))
                    ctokens.append((t, "$%s" % v))
                    ctokens.append((Token.Operator, "+"))
                    ctokens.append((Token.Literal.Number, "%d" % len(self.bytecode)))
                    ctokens.append((Token.Punctuation, ")"))
                else:
                    ctokens.append((t, "$%s" % v))

            else:
                ctokens.append((t, v))

        return ctokens, relative

    def _convert_att(self, tokens):

        relative = True
        ctokens = []
        args = []

        for t, v in tokens:

            if v == "*":
                relative = False

            elif v == "(":

                base = ctokens
                ctokens = []

                ctokens.append((Token.Operator, "*"))
                ctokens.append((Token.Punctuation, "("))

                # should convert types to cast here.
                ctokens.append((Token.Keyword.Type, "void"))
                ctokens.append((Token.Operator, "*"))

                ctokens.append((Token.Operator, "*"))
                ctokens.append((Token.Punctuation, ")"))
                ctokens.append((Token.Punctuation, "("))

                ctokens.extend(base)

                args = [(Token.Operator, "+"),
                        (Token.Operator, "+"),
                        (Token.Operator, "*")]

            elif v == ")":
                ctokens.append((Token.Punctuation, ")"))
                args = []

            elif v == ",":
                del args[0]

            elif t is Token.Operator:
                ctokens.append((t, v))

            else:

                # This is the case where we want to insert
                # argument operators if there are any.

                if args:
                    ctokens.append(args[0])

                if t is Token.Name.Variable:

                    if v.startswith("%"):
                        v = "$%s" % v[1:]

                    if (v == "$riz" or v == "$eiz"):
                        ctokens.append((Token.Literal.Number, "0"))

                    elif v in ("$eip", "$rip", "$pc"):
                        ctokens.append((Token.Punctuation, "("))
                        ctokens.append((t, "%s" % v))
                        ctokens.append((Token.Operator, "+"))
                        ctokens.append((Token.Literal.Number, "%d" % len(self.bytecode)))
                        ctokens.append((Token.Punctuation, ")"))
                    else:
                        ctokens.append((t, v))

                else:
                    ctokens.append((t, v))

        return ctokens, relative

    def get_expression(self):

        types = []
        tokens = []

        start = self.instidx
        while self.tokens[start][0] is not Token.Text:
            start += 1

        for t, v in self.tokens[start:]:
            if tokens and t is Token.Text:
                break
            if t is Token.Text:
                pass
            elif t is Token.Keyword.Type:
                types.append((t, v))
            else:
                tokens.append((t, v))

        if disassemblyflavor.value == "intel":
            ctokens, relative = self._convert_intel(tokens)
        elif disassemblyflavor.value == "att":
            ctokens, relative = self._convert_att(tokens)
        else:
            assert False, "not intel or att."

        if relative:
            if not len(ctokens) == 1 and ctokens[0][0] is Token.Number.Integer:

                ctokens = [(Token.Name.Variable, "$pc"),
                           (Token.Operator, "+")
                           ] + ctokens

        return gxf.Expression(ctokens)

    def get_heading(self, stack="$rsp"):

        # We need three primitives:
        #   compute_jmp_addr  (flags + expression)
        #   compute_ret_addr  (from stack)
        #   compute_call_addr (expression)

        if self.itype is RET:
            return gxf.parse_and_eval("*(void **) (%s)" % stack)

        if self.itype is CALL:
            exp = self.get_expression()
            val = exp.eval()
            return val

        if self.itype is JMP and check_flags(self.inst):
            exp = self.get_expression()
            val = exp.eval()
            return val


class DisassemblyBlock(gxf.Formattable):

    # TODO: lexing is slow (seems legit)
    # check if we can speed this up.

    def __init__(self, disassembly, lexer=lexer, msg=None):

        self.lines = []
        if isinstance(disassembly, list):
            self.lines = disassembly
        elif disassembly:
            line = []
            if msg:
                current_function = msg.rsplit(None, 1)[-1][:-1]
            else:
                current_function = None
            with currentfunctiontfilter.current_function(current_function):
                for ttype, value in pygments.lex(disassembly, lexer):
                    if '\n' in value:
                        self.lines.append(DisassemblyLine(line))
                        line = []
                    else:
                        line.append((ttype, value))

        self.linenos = {}
        for i, line in enumerate(self.lines):
            self.linenos[line.address] = line, i

        self.lexer = lexer
        self.msg = msg

    def get_lineno_for_addr(self, addr):
        best = None, None
        for i, line in enumerate(self.lines):
            if line.address > addr:
                break
            best = line, i
        return best

    def fmttokens(self, hexdump=False, start=None, stop=None):
        for line in self.lines[start:stop]:
            yield from line.fmttokens(hexdump=hexdump)
            yield (Token.Text, "\n")

    def output(self, *args, **kwargs):
        print(self.format(*args, **kwargs), end="")

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, key):
        assert isinstance(key, slice)
        key = slice(max(key.start, 0), key.stop, 1)
        return DisassemblyBlock(self.lines[key], self.lexer, self.msg)

    def __iter__(self):
        yield from self.lines


# _disassemble is a direct wrapper for gdb's disassemble.

def _disassemble(startaddr, endaddr=None, hexdump=True, ignmemerr=False):
    # TODO: We might want to use Architecture.disassemble
    # problems with that:
    #   - not sure how to get hexdump
    #   - we can't limit on function bounds as we do now.

    modifier = " /r" if hexdump else ""
    what = ",".join(hex(int(addr)) for addr in (startaddr, endaddr) if addr)
    try:
        data = gxf.execute("disassemble%s %s" % (modifier, what), False, True)
    except gxf.MemoryError as e:
        if not ignmemerr:
            raise
        # if failaddr == startaddr this will return nothing.
        return _disassemble(startaddr, e.address, hexdump)

    start, end = data.find('\n') + 1, data.rfind('\n', 0, -1)
    return data[start:end], data[:start - 1]


def disassemble(startaddr, endaddr=None, ignmemerr=False):
    data, msg = _disassemble(startaddr, endaddr, True, ignmemerr)
    return DisassemblyBlock(data, msg=msg)


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


def disassemble_lines(addr, count=1, offset=0, ignfct=False):
    addr = int(addr)

    if ignfct is False:

        try:
            disfct = disassemble(addr)
            _, ln = disfct.get_lineno_for_addr(addr)
            assert ln is not None, "addr should be in function."
            # If offset is outside of function we don't to fallback.
            # If the user wanted that he should have:
            #   - used ignfct if he wanted an exact match (if possible).
            #   - passed addr=addr+offset if he wanted results
            #     always including addr. .
            return disfct[ln + offset:ln + offset + count]
        except gxf.MemoryError:
            # Nothing we can do about this.
            raise
        except gdb.error:
            # This probably means the address is not in a function
            # we need to fallback on the harder method.
            pass

    if offset >= 0:
        # plain old linear sweep.
        disafter = disassemble(addr, addr + offset * 16 + count * 16,
                               ignmemerr=True)
        return disafter[offset:offset + count]

    # Now we need to use backwards disassembling hacks :-)

    # 64 additional bytes gives it time to automagically sync:
    backguess = addr + offset * 16 - 64

    # The following pattern has false positives, its not a problem.
    hexaddr = "%x" % addr

    badblocks = []
    baddr, bdata, bmsg = None, None, None
    check = False

    guesslimit = backguess + 16
    while backguess < guesslimit:

        try:
            data, msg = _disassemble(backguess, addr + count * 16,
                                     ignmemerr=False)
        except gxf.MemoryError as e:
            # Shit, we're on the edge. We don't know how far, both directions
            # might take a realy long time without a way to know if we will
            # endup hitting something.
            # To address this we do a binary search at this point and fast
            # forward backguess and adjust guesslimit to 16.

            # We do sacrifice log2(N) disassemblies. (sorry about that...)

            # There is a twist to this binary search: We try to snap to
            # 2**10 boundaries when crossed, there is a good chance that's
            # the place we're looking for anyway. That means two things:
            # - if % align was succesfull check % align - 1 instead of /2.
            # - elif % align in what we're skipping check it instead of /2.

            align = 4096

            validmem = addr
            # we know current backguess is invalid, start at:
            nextguess = backguess + (validmem - backguess) // 2

            while backguess != nextguess:

                try:
                    _disassemble(nextguess, addr + count * 16, ignmemerr=False)
                except gxf.MemoryError as e:
                    backguess = nextguess
                else:
                    validmem = nextguess

                # if we cross a boundary, we want to snap to the align.

                if backguess == nextguess and nextguess % align == align - 1:
                    # If we failed right before the boundary check we now
                    # must check the boundary itself.
                    nextguess += 1

                else:
                    # Otherwise normal split.
                    nextguess = backguess + (validmem - backguess) // 2

                    # But try to snap to boundary - 1 if possible:
                    # (then when it fails we'll be able to check next one.)
                    crossing = nextguess - (nextguess % align) + align - 1
                    if backguess < crossing < validmem:
                        nextguess = crossing


            # Ok new limits after BS, we need to start this over:
            backguess = validmem
            guesslimit = backguess + 16
            continue


        if hexaddr in data:
            check = _check_data(data, addr)
            if check is True:
                break
            if check is not None and (baddr is None or check < baddr):
                baddr, bdata, bmsg = check, data, msg

        backguess += 1

    if check is True:
        # Ok be found something already.
        pass

    elif bdata is not None:
        # No dice, lets check if we have some matching targets that
        # simply have some (bad)s. We'll take the furthest away.
        data, msg = bdata, bmsg

    else:
        # This stream's target address is probably fucked up, otherwise
        # we would have synced already. Lets try this from the target,
        # then we'll know soon if it is even possible to get there.

        check = None
        bads = 0

        # We start at addr, that should give us at least one good one.
        for backguess in range(addr, addr + offset * 16 - 1, -1):

            try:
                bdata, bmsg = _disassemble(backguess, backguess + count * 16,
                                           ignmemerr=False)
            except gxf.MemoryError as e:
                break

            if hexaddr in bdata and _check_data(bdata, addr) is not None:
                # New best thing?
                data, msg = bdata, bmsg
                bads = 0
            elif bads == 15:
                # We will never hit it again.
                break
            else:
                bads += 1

    disassembly = DisassemblyBlock(data, msg=msg)
    _, ln = disassembly.linenos[addr]
    assert ln is not None, "addr should be in function."
    return disassembly[ln + offset:ln + offset + count]


def disassemble_heading(addr, count=10, offset=0):

    if offset > 0:
        raise NotImplementedError("heading w/ offset > 0")

    addr = int(addr)

    trunk = disassemble_lines(addr, count, offset, ignfct=True)
    branch = None

    heading = None

    future, stop = None, None

    for i, line in enumerate(trunk):

        if i < -offset:
            # not interested in headings before current addr.
            continue

        heading = line.get_heading()
        if heading is not None:
            branch = i + 1
            break

    # We're not interested if branch is last line.
    if heading and branch < count:

        future = disassemble_lines(heading, count - i, ignfct=True)
        for i, line in enumerate(future):
            if line.itype is RET:
                stop = i
                break

    return trunk, branch, future, stop
