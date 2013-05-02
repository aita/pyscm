# coding:utf-8

import subprocess
import tempfile
import pytest
from pyscm import compiler

ASM_FILENAME = "stst.s"


def run_compile(expr):
    with open(ASM_FILENAME, 'w') as fp:
        c = compiler.Compiler(fp)
        c.compile_program(expr)


def build_program(expr):
    run_compile(expr)
    build()


def build():
    subprocess.call(["gcc", "ctest.c", ASM_FILENAME, "-o", "ctest"])


def execute():
    proc = subprocess.Popen(["./ctest"], stdout=subprocess.PIPE)
    return proc.stdout.read()
    

@pytest.mark.parametrize(('expr', 'result'), [
    (1, '1\n'),
    (2, '2\n'),
    (3, '3\n'),
    (42, '42\n'),
])
def test_with_execute(expr, result):
    run_compile(expr)
    build()
    assert execute() == result

    
