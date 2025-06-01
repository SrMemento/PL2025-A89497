class Program:
    def __init__(self, name, block):
        self.name = name
        self.block = block

class Block:
    def __init__(self, declarations, statements):
        self.declarations = declarations
        self.statements = statements

class VarDecl:
    def __init__(self, name, vartype):
        self.name = name
        self.vartype = vartype

class Assignment:
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

class If:
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class For:
    def __init__(self, var, start, end, body, downto=False):
        self.var = var
        self.start = start
        self.end = end
        self.body = body
        self.downto = downto

class Compound:
    def __init__(self, statements):
        self.statements = statements

class BinaryOp:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Var:
    def __init__(self, name):
        self.name = name

class Const:
    def __init__(self, value):
        self.value = value

class WriteLn:
    def __init__(self, exprs):
        self.exprs = exprs  # Lista de expressões

class Write:
    def __init__(self, exprs):
        self.exprs = exprs  # Lista de expressões a serem escritas

class ReadLn:
    def __init__(self, exprs):
        self.exprs = exprs  # Lista de expressões a serem lidas

class ArrayType:
    def __init__(self, start_idx, end_idx, base_type):
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.base_type = base_type

    def __repr__(self):
        return f"ArrayType[{self.start_idx}..{self.end_idx}] of {self.base_type}"

class ArrayAccess:
    def __init__(self, array_var, index_expr):
        self.array_var = array_var
        self.index_expr = index_expr

class FunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FunctionCall({self.name}, {self.args})"

class FunctionDecl:
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params  # lista de tuplos (nome, tipo)
        self.return_type = return_type
        self.body = body
