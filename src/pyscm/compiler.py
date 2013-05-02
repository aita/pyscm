# coding: utf-8

import sys

WORDSIZE = 4
FIXNUM_SHIFT = 2
FIXNUM_MASK = 0x00
FIXNUM_BITS = WORDSIZE*4 - FIXNUM_SHIFT
FIXNUM_MIN = -(2 ** (FIXNUM_BITS-1))
FIXNUM_MAX = 2 ** (FIXNUM_BITS-1) -1
BOOL_F = 0x2F
BOOL_T = 0x6F
CHAR_MASK = 0x0F
CHAR_SHIFT = 8
CHAR_BITS = WORDSIZE*4 - CHAR_SHIFT
CHAR_MIN = -(2 ** (CHAR_BITS-1))
CHAR_MAX = 2 ** (CHAR_BITS-1) -1
NIL = 0x3F


class CompileError(Exception):
    pass


def isfixnum(expr):
    return all([isinstance(expr, int),
                FIXNUM_MIN <= expr <= FIXNUM_MAX])


def isboolean(expr):
    return isinstance(expr, bool)


def ischar(expr):
    if isinstance(expr, basestring):
        return len(expr) == 1 and CHAR_MIN <= ord(expr) <= CHAR_MAX
    return False

def isnil(expr):
    return expr == None


def isimmediate(expr):
    return any([
        isboolean(expr),
        isfixnum(expr),
        ischar(expr),
        isnil(expr),
    ])
    

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
    elif isnil(expr):
        return NIL
        

class Compiler(object):

    def __init__(self, out):
        self.out = out
    
    def emit(self, asm):
        self.out.write("\t%s\n" % asm)
    
    def emit_program(self, expr):
        if isimmediate(expr):
            self.emit("movl	${}, %eax".format(immediate_rep(expr)))
            self.emit("ret")
        else:
            raise CompileError("%s is not integer" % expr)
    
    def compile_program(self, x):
        self.out.write("""\
    .text
    .globl    scheme_entry
    .type    scheme_entry, @function
scheme_entry:\n""")
        self.emit_program(x)
        self.out.write("    .size    scheme_entry, .-scheme_entry\n")
