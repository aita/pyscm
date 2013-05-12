# coding:utf-8

premitives = {}

def premitive(name):
    def _premitive(f):
        premitives[name] = f
        return f
    return _premitive


@premitive('fxadd1')
def _(c, arg):
    c.emit_expr(arg)
    c.emit("    and %s, %al" % immediate_rep)
    
