# coding: utf-8

import sys
from pyscm import parser
from pyscm.parser import Symbol


WORDSIZE = 4
FIXNUM_SHIFT = 2
FIXNUM_BITS = WORDSIZE*4 - FIXNUM_SHIFT
FIXNUM_TAG = 0x00
FIXNUM_MASK = 0x03 # 0b00000011
FIXNUM_MIN = -(2 ** (FIXNUM_BITS-1))
FIXNUM_MAX = 2 ** (FIXNUM_BITS-1) -1
BOOL_BITS = 6
BOOL_F = 0x2F    # 0b00101111
BOOL_T = 0x6F    # 0b01101111
BOOL_MASK = 0xBF # 0b10111111
CHAR_SHIFT = 8
CHAR_TAG = 0x0F  # 0b00001111
CHAR_MASK = 0x0F # 0b00001111
CHAR_BITS = WORDSIZE*4 - CHAR_SHIFT
CHAR_MIN = -(2 ** (CHAR_BITS-1))
CHAR_MAX = 2 ** (CHAR_BITS-1) -1
NULL = 0x3F # b00111111


FUNCTION_HEADER = """\
    .text
    .globl    {name}
    .type    {name}, @function
{name}:\n"""


class CompileError(Exception):
    pass


primitives = {}


def primitive(name):
    "define primitive procedure"
    def _primitive(f):
        primitives[name] = f
        return f
    return _primitive


def isprimitive(expr):
    return issymbol(expr) and expr.name in primitives


def isprimcall(expr):
    return isinstance(expr, list) and isprimitive(expr[0])


def issymbol(expr):
    return isinstance(expr, Symbol)
    

def isfixnum(expr):
    return all([isinstance(expr, int),
                FIXNUM_MIN <= expr <= FIXNUM_MAX])


def isboolean(expr):
    return isinstance(expr, bool)


def ischar(expr):
    if isinstance(expr, basestring):
        return len(expr) == 1 and CHAR_MIN <= ord(expr) <= CHAR_MAX
    return False

def isnull(expr):
    return expr == None


def isimmediate(expr):
    return any([
        isboolean(expr),
        isfixnum(expr),
        ischar(expr),
        isnull(expr),
    ])


def isif(expr):
    if isinstance(expr, list):
        if len(expr) == 4 and isinstance(expr[0], Symbol):
            return expr[0].name == 'if'
    return False


def if_test(expr):
    return expr[1]


def if_conseq(expr):
    return expr[2]


def if_altern(expr):
    return expr[3]


def isand(expr):
    if isinstance(expr, list):
        if len(expr) > 0 and isinstance(expr[0], Symbol):
            return expr[0].name == 'and'
    return False


def isor(expr):
    if isinstance(expr, list):
        if len(expr) > 0 and isinstance(expr[0], Symbol):
            return expr[0].name == 'or'
    return False


def immediate_rep(expr):
    if isboolean(expr):
        if expr == True:
            return BOOL_T
        else:
            return BOOL_F
    elif isfixnum(expr):
        return expr << FIXNUM_SHIFT
    elif ischar(expr):
        return (ord(expr) << CHAR_SHIFT) | CHAR_MASK
    elif isnull(expr):
        return NULL


@primitive('fxadd1')
def _(c, si, arg):
    c.emit_expr(si, arg)
    c.emit("    addl ${}, %eax", immediate_rep(1))


@primitive('fixnum?')
def _(c, si, arg):
    c.emit_expr(si, arg)
    # %eax = (x & FIXNUM_MASK) == FIXNUM_TAG
    c.emit("    and ${}, %al", FIXNUM_MASK)
    c.emit("    cmp ${}, %al", FIXNUM_TAG)
    c.emit_cmp_boolean()


@primitive('fxsub1')
def _(c, si, arg):
    c.emit_expr(si, arg)
    c.emit("    subl ${}, %eax", immediate_rep(1))


@primitive('fixnum->char')
def _(c, si, arg):
    c.emit_expr(si, arg)
    c.emit("    shll ${}, %eax", CHAR_SHIFT - FIXNUM_SHIFT)
    c.emit("    orl ${}, %eax", CHAR_TAG)

    
@primitive('char->fixnum')
def _(c, si, arg):
    c.emit_expr(si, arg)
    c.emit("    shrl ${}, %eax", CHAR_SHIFT - FIXNUM_SHIFT)


@primitive('fxzero?')
def _(c, si, arg, cmp_boolean=True):
    c.emit_expr(si, arg)
    c.emit("    cmp ${}, %eax", immediate_rep(0))
    if cmp_boolean:
        c.emit_cmp_boolean()


@primitive('null?')
def _(c, si, arg, cmp_boolean=True):
    c.emit_expr(si, arg)
    c.emit("    cmp ${}, %eax", NULL)
    if cmp_boolean:
        c.emit_cmp_boolean()


@primitive('boolean?')
def _(c, si, arg, cmp_boolean=True):
    c.emit_expr(si, arg)
    c.emit("    and ${}, %al", BOOL_MASK)
    c.emit("    cmp ${}, %al", BOOL_F)
    if cmp_boolean:
        c.emit_cmp_boolean()


@primitive('not')
def _(c, si, arg):
    c.emit_expr(si, arg)
    c.emit("    cmp ${}, %al", BOOL_F)
    c.emit_cmp_boolean()


@primitive('fxlognot')
def _(c, si, arg):
    c.emit_expr(si, arg)
    c.emit("    notl %eax")
    c.emit("    xorl ${}, %eax", FIXNUM_MASK)


@primitive('fx+')
def _(c, si, arg1, arg2):
    c.emit_binop(si, arg1, arg2)
    c.emit("    addl {}(%esp), %eax", si)


@primitive('fx-')
def _(c, si, arg1, arg2):
    c.emit_binop(si, arg2, arg1)
    c.emit("    subl {}(%esp), %eax", si)


@primitive('fxlogand')
def _(c, si, arg1, arg2):
    c.emit_binop(si, arg1, arg2)
    c.emit("    andl {}(%esp), %eax", si)


@primitive('fxlogor')
def _(c, si, arg1, arg2):
    c.emit_binop(si, arg1, arg2)
    c.emit("    or {}(%esp), %eax", si)


@primitive('fxlogor')
def _(c, si, arg1, arg2):
    c.emit_binop(si, arg1, arg2)
    c.emit("    or {}(%esp), %eax", si)


@primitive('fx=')
def _(c, si, arg1, arg2):
    c.emit_cmp_binop(si, arg1, arg2)
    c.emit_cmp_boolean()


class Compiler(object):

    def __init__(self, out):
        self.out = out
        self.count = 0

    def unique_label(self):
        label = "L_%d" % self.count
        self.count += 1
        return label
    
    def emit(self, asm, *args, **kwargs):
        self.out.write(asm.format(*args, **kwargs))
        self.out.write("\n")

    def emit_immediate(self, expr):
        self.emit("    movl ${}, %eax", immediate_rep(expr))

    def emit_primcall(self, si, expr, **opt):
        sym = expr[0]
        prim = primitives[sym.name]
        # arg = expr[1:]
        # if len(arg) == prim.func_code.co_argcount+1:
        #     raise CompileError()
        arg = expr[1:]
        prim(self, si, *arg, **opt)

    def emit_if(self, si, expr):
        alt_label = self.unique_label()
        end_label = self.unique_label()
        test_expr = if_test(expr)
        if isprimcall(test_expr) and test_expr[0].name[-1] == '?':
            self.emit_primcall(test_expr, cmp_boolean=False)
        else:
            self.emit_expr(si, test_expr)
            self.emit("    cmp ${}, %al", BOOL_F)
        self.emit("    je {}", alt_label)
        self.emit_expr(si, if_conseq(expr))
        self.emit("    jmp {}", end_label)
        self.emit("{}:", alt_label)
        self.emit_expr(si, if_altern(expr))
        self.emit("{}:", end_label)

    def emit_and(self, si, expr):
        if len(expr) == 1:
            self.emit_immediate(True)
        elif len(expr) == 2:
            self.emit_expr(si, expr[1])
        else:
            self.emit_if(si, [
                Symbol('if'),
                expr[1],
                [Symbol('and')] + expr[2:],
                False,
            ])

    def emit_or(self, si, expr):
        if len(expr) == 1:
            self.emit_immediate(True)
        elif len(expr) == 2:
            self.emit_expr(si, expr[1])
        else:
            self.emit_if(si, [
                Symbol('if'),
                expr[1],
                expr[1],
                [Symbol('or')] + expr[2:],
            ])

    def emit_binop(self, ci, arg1, arg2):
        self.emit_expr(si, arg1)
        self.emit("    movl %eax, {}(%esp)", si)
        self.emit_expr(si-WORDSIZE, arg2)

    def emit_cmp_binop(self, ci, arg1, arg2):
        self.emit_binop(self, ci, arg1, arg2)
        c.emit("    cmp {}(%esp), %eax", si)        

    def emit_expr(self, si, expr):
        if isimmediate(expr):
            self.emit_immediate(expr)
        elif isif(expr):
            self.emit_if(si, expr)
        elif isand(expr):
            self.emit_and(si, expr)
        elif isor(expr):
            self.emit_or(si, expr)
        elif isprimcall(expr):
            self.emit_primcall(si, expr)
        else:
            raise CompileError("Unknown Type: %s" % expr)

    def emit_function_header(self, name):
        self.emit(FUNCTION_HEADER.format(name=name))

    def emit_cmp_boolean(self):
        self.emit("    sete %al")
        self.emit("    movzbl %al, %eax")
        # %eal = (%eal << BOOL_BIT) | BOOL_F
        # (x << 6) | b00101111
        self.emit("    sal ${}, %al", BOOL_BITS)
        self.emit("    or ${}, %al", BOOL_F)
    
    def emit_program(self, expr):
        self.emit_function_header("L_scheme_entry")
        self.emit_expr(-WORDSIZE, expr)
        self.emit("    ret")
        self.emit_function_header("scheme_entry")
        self.emit("    movl %esp, %ecx")
        self.emit("    movl 4(%esp), %esp")
        self.emit("    call L_scheme_entry")
        self.emit("    movl %ecx, %esp")
        self.emit("    ret")
        
    def compile_program(self, s):
        self.emit_program(parser.read(s))


if __name__ == "__main__":
    import sys, tempfile, subprocess
    c = Compiler(sys.stdout)
    c.compile_program(sys.stdin.read())
