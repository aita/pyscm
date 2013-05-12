# coding:utf-8
import sys, os
import re
from funcparserlib.lexer import make_tokenizer, Token, LexerError
from funcparserlib.parser import some, a, maybe, many, skip, oneplus, forward_decl as fwd
from collections import namedtuple


Symbol = namedtuple('Symbol', 'name')


def tok(type, value=None):
    return a(Token(type, value))

const = lambda x: lambda _: x
flatten = lambda list: sum(list, [])
unarg = lambda f: lambda args: f(*args)

# Auxiliary functions for lexers
tokval = lambda tok: tok.value

# Auxiliary functions for parsers
mktok = lambda type: lambda value: tok(type, value) >> tokval
n = mktok('name')
n_ = lambda s: skip(op(s))
op = mktok('op')
op_ = lambda s: skip(op(s))
# sometok = lambda type: tok(type) >> tokval
sometok = lambda t: some(lambda x: x.type == t) >> tokval


def tokenizer(str):
    'str -> Sequence(Token)'
    specs = [
        ('space',  (r'[ \t\r\n]+',)),
        ('int', (r'-?[1-9][0-9]*|0',)),
        ('true', (r'#t',)),
        ('false', (r'#f',)),
        ('char', (r'#\\[A-Za-z_0-9]',)),
        ('op', (r'[\[\]\(\)\']', re.VERBOSE)),
        ('name', (r'[A-Za-z_0-9\&\*\+\-\~!\=<>\^/,\?:;.]*',)),
    ]
    useless = ['space']
    t = make_tokenizer(specs)
    return [x for x in t(str) if x.type not in useless]


sexpr = fwd()
integer = sometok('int') >> int
symbol = sometok('name') >> Symbol
true = sometok('true') >> const(True)
false = sometok('false') >> const(False)
boolean = true | false
char = sometok('char') >> (lambda x: x[2])
dotlist = op_('(') + many(sexpr) + op_(')') >> (lambda x: x or None)
quote = op_('\'') + sexpr >> (lambda x: [Symbol('quote'), sexpr])
sexpr.define(
    integer
    | symbol
    | boolean
    | char
    | dotlist
)


def read(s):
    "str -> SExpr"
    return sexpr.parse(tokenizer(s))
