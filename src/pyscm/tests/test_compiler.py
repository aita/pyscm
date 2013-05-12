# coding:utf-8

import subprocess
import tempfile
import pytest
from pyscm import compiler

ASM_FILENAME = "stst.s"

expr_and_result = [
    (r'1', '1\n'),
    (r'2', '2\n'),
    (r'3', '3\n'),
    (r'42', '42\n'),
    (r'#t', '#t\n'),
    (r'#f', '#f\n'),
    (r'#\a', '#\\a\n'),
    (r'#\z', '#\\z\n'),
    (r'()', '()\n'),
    (r'(fxadd1 1)', '2\n'),
    (r'(fxsub1 1)', '0\n'),
    (r'(fixnum->char 97)', '#\\a\n'),
    (r'(fixnum? 1)', '#t\n'),
    (r'(fixnum? 37)', '#t\n'),
    (r'(fixnum? #t)', '#f\n'),
    (r'(fixnum? #f)', '#f\n'),
    (r'(fixnum? ())', '#f\n'),
    (r'(fxzero? 1)', '#f\n'),
    (r'(fxzero? 0)', '#t\n'),
    (r'(null? 0)', '#f\n'),
    (r'(null? ())', '#t\n'),
    (r'(char->fixnum #\a)', '97\n'),
    (r'(char->fixnum #\A)', '65\n'),
    (r'(boolean? #f)', '#t\n'),
    (r'(boolean? #t)', '#t\n'),
    (r'(boolean? 1)', '#f\n'),
    (r'(boolean? #\a)', '#f\n'),
    (r'(not #t)', '#f\n'),
    (r'(not #f)', '#t\n'),
    (r'(not 1)', '#f\n'),
    (r'(fxlognot 1)', '-2\n'), 
    (r'(fxlognot -1)', '0\n'),
    (r'(if #t #t #f)', '#t\n'),
    (r'(if #f #t #f)', '#f\n'),
    (r'(and)', '#t\n'),
    (r'(and 1)', '1\n'),
    (r'(and 1 #f 3)', '#f\n'),
    (r'(and 1 3 3)', '3\n'),
    (r'(and 1 3 #f)', '#f\n'),
    (r'(or)', '#t\n'),
    (r'(or 1)', '1\n'),
    (r'(or 1 #f 1)', '1\n'),
    (r'(or #f 3 3)', '3\n'),
    (r'(or 1 3 #f)', '1\n'),
    (r'(fx+ 1 2)', '3\n'),
    (r'(fx- 3 1)', '2\n'),
    (r'(fxlogand 3 1)', '1\n'),
    (r'(fxlogand 3 2)', '2\n'),
    (r'(fxlogor 2 1)', '3\n'),
    (r'(fxlogor 4 2)', '6\n'),
    (r'(fx= 4 2)', '#f\n'),
    (r'(fx= 2 2)', '#t\n'),
]


def run_compile(expr):
    with open(ASM_FILENAME, 'w') as fp:
        c = compiler.Compiler(fp)
        c.compile_program(expr)


def build_program(expr):
    run_compile(expr)
    build()


def build():
    subprocess.call(["gcc", "runtime.c", ASM_FILENAME, "-o", "ctest"])


def execute():
    proc = subprocess.Popen(["./ctest"], stdout=subprocess.PIPE)
    return proc.stdout.read()


@pytest.mark.parametrize(('expr', 'result'), expr_and_result)
def test_execute(expr, result):
    run_compile(expr)
    build()
    assert execute() == result

    
# @pytest.mark.parametrize(('expr', 'error'), [
#     # ('hello', compiler.CompileError),
# ])
# def test_compile_failure(expr, error):
#     with pytest.raises(error):
#         run_compile(expr)
