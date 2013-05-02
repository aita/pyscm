# coding: utf-8

import sys

class CompileError(Error):
    pass


class Compiler(object):

    def __init__(self, out):
        self.out = out
    
    def emit(self, asm):
        self.out.write("\t%s\n" % asm)
    
    def emit_program(self, expr):
        if isinstance(expr, int):
            self.emit("movl	${}, %eax".format(expr))
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
