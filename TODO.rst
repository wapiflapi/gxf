This is most of the commands of peda categorized by gdb command type.
This servers as a todo list :-) We should remove the ones we implemented,
it's not hard to generate such a list from the implement commands if needed.



gdb.COMMAND_NONE
================
The command does not belong to any particular
class. A command in this category will not be displayed in any of the help
categories.


gdb.COMMAND_RUNNING
===================
The command is related to running the inferior. For example, start, step, and
continue are in this category. Type help running at the GDB prompt to see a list
of commands in this category.

skip:             Skip execution of next count instructions
start:            Start debugged program and stop at most convenient entry
nextcall:         Step until next 'call' instruction in specific memory range
nextjmp:          Step until next 'j*' instruction in specific memory range
stepuntil:        Step until a desired instruction in specific memory range
xuntil:           Continue execution until an address or function

goto:             Continue execution at an address


gdb.COMMAND_DATA
================
The command is related to data or variables. For example, call, find, and print
are in this category. Type help data at the GDB prompt to see a list of commands
in this category.

context:          Display various information of current execution context
context_code:     Display nearby disassembly at $PC of current execution context
context_register: Display register information of current execution context
context_stack:    Display stack of current execution context

dumpargs:         Display arguments passed to a function when stopped at a call
                  instruction
eflags:           Display/set/clear value of eflags register

vmmap:            Get virtual mapping address ranges of section(s) in debugged
                  process

asmsearch:        Search for ASM instructions in memory
cmpmem:           Compare content of a memory region with a file
distance:         Calculate distance between two addresses
dumpmem:          Dump content of a memory region to raw binary file
hexdump:          Display hex/ascii dump of data in memory
hexprint:         Display hexified of data in memory
jmpcall:          Search for JMP/CALL instructions in memory
loadmem:          Load contents of a raw binary file to memory
dumprop:          Dump all ROP gadgets in specific memory range
lookup:           Search for all addresses/references to addresses which belong
                  to a memory range
refsearch:        Search for all references to a value in memory ranges

pdisass:          Format output of gdb disassemble command with colors
nearpc:           Disassemble instructions nearby current PC or given address

patch:            Patch memory start at an address with string/hexstring/int

searchmem:        Search for a pattern in memory; support regex search
sgrep:            Search for full strings contain the given pattern
strings:          Display printable strings in memory
substr:           Search for substrings of a given string/number in memory
telescope:        Display memory content at an address with smart dereferences

xinfo:            Display detail information of address/registers
xormem:           XOR a memory region with a key
xprint:           Extra support to GDB's print command
xrefs:            Search for all call/data access references to a
                  function/variable


gdb.COMMAND_STACK
=================
The command has to do with manipulation of the stack. For example, backtrace,
frame, and return are in this category. Type help stack at the GDB prompt to see
a list of commands in this category.


gdb.COMMAND_FILES
=================
This class is used for file-related commands. For example, file, list and
section are in this category. Type help files at the GDB prompt to see a list of
commands in this category.

checksec:         Check for various security options of binary
elfheader:        Get headers information from debugged ELF file
elfsymbol:        Get non-debugging symbol information from an ELF file
readelf:          Get headers information from an ELF file


gdb.COMMAND_SUPPORT
===================
This should be used for “support facilities”, generally meaning things that are
useful to the user when interacting with GDB, but not related to the state of
the inferior. For example, help, make, and shell are in this category. Type help
support at the GDB prompt to see a list of commands in this category.

assemble:         On the fly assemble and execute instructions using NASM
gennop:           Generate abitrary length NOP sled using given characters

shellcode:        Generate or download common shellcodes.
skeleton:         Generate python exploit code template

pattern:          Generate, search, or write a cyclic pattern to memory
pattern_arg:      Set argument list with cyclic pattern
pattern_create:   Generate a cyclic pattern
pattern_env:      Set environment variable with a cyclic pattern
pattern_offset:   Search for offset of a value in cyclic pattern
pattern_patch:    Write a cyclic pattern to memory
pattern_search:   Search a cyclic pattern in registers and memory

session:          Save/restore a working gdb session to file as a script
snapshot:         Save/restore process's snapshot to/from file
crashdump:        Display crashdump info and save to file


gdb.COMMAND_STATUS
==================
The command is an ‘info’-related command, that is, related to the state of GDB
itself. For example, info, macro, and show are in this category. Type help
status at the GDB prompt to see a list of commands in this category.

aslr:             Show/set ASLR setting of GDB
getfile:          Get exec filename of current debugged process
getpid:           Get PID of current debugged process
procinfo:         Display various info from /proc/pid/


gdb.COMMAND_BREAKPOINTS
=======================
The command has to do with breakpoints. For example, break, clear, and delete
are in this category. Type help breakpoints at the GDB prompt to see a list of
commands in this category.

pltbreak:         Set breakpoint at PLT functions match name regex
deactive: (?)     Bypass a function by ignoring its execution (eg sleep/alarm)


gdb.COMMAND_TRACEPOINTS
=======================
The command has to do with tracepoints. For example, trace, actions, and tfind
are in this category. Type help tracepoints at the GDB prompt to see a list of
commands in this category.

profile:          Simple profiling to count executed instructions in the program
tracecall:        Trace function calls made by the program
traceinst:        Trace specific instructions executed by the program


gdb.COMMAND_USER
================
The command is a general purpose command for the user, and typically does not
fit in one of the other categories. Type help user-defined at the GDB prompt to
see a list of commands in this category, as well as the list of gdb macros (see
Sequences).


gdb.COMMAND_OBSCURE
===================
The command is only used in unusual circumstances, or is not of general interest
to users. For example, checkpoint, fork, and stop are in this category. Type
help obscure at the GDB prompt to see a list of commands in this category.


gdb.COMMAND_MAINTENANCE
=======================
The command is only useful to GDB maintainers. The maintenance and flushregs
commands are in this category. Type help internals at the GDB prompt to see a
list of commands in this category.

