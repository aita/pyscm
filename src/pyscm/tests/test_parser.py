# coding:utf-8

import pytest
from pyscm import parser


@pytest.mark.parametrize(('sexpr', 'result'), [
    ('132', 132),
    ('(1 2 3)', [1,2,3]),
    ('#t', True),
    ('#f', False),
    ('#\\a', 'a'),
    ('#\\b', 'b'),
    ('()', None),
])
def test_sexpr(sexpr, result):
    assert result ==  parser.sexpr.parse(parser.tokenizer(sexpr))
