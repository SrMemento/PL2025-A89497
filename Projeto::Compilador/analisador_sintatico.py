import sys
import ply.yacc as yacc
from analisador_lexico import tokens  # Importa os tokens do analisador léxico
import ast_nodes as ast

# ----------------------
# Precedência (como antes)
# ----------------------
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'NOT'),
    ('left', '=', '<', '>', 'LE', 'GE', 'NE'),
    ('left', '+', '-'),
    ('left', '*', '/', 'DIV', 'MOD'),
)

# ----------------------
# Produções com AST
# ----------------------

def p_program(p):
    'program : PROGRAM ID ";" block "."'
    p[0] = ast.Program(p[2], p[4])

def p_block(p):
    '''block : declarations BEGIN optional_statements END'''
    p[0] = ast.Block(p[1], p[3])

def p_optional_statements(p):
    '''optional_statements : statements
                           | empty'''
    p[0] = p[1]

def p_declarations(p):
    '''declarations : declarations declaration
                    | declaration
                    | empty'''
    if len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 2:
        p[0] = p[1] if p[1] else []
    else:
        p[0] = []

def p_declaration(p):
    '''declaration : VAR var_declarations
                   | function_declaration'''
    if len(p) == 3:
        p[0] = p[2]  # var declarations
    else:
        p[0] = p[1]

def p_var_declarations(p):
    '''var_declarations : var_declarations var_declaration
                        | var_declaration'''
    if len(p) == 3:
        p[0] = p[1] + p[2]  # ← aqui p[2] é uma lista
    else:
        p[0] = p[1]

def p_function_declaration(p):
    '''function_declaration : FUNCTION ID '(' param_list_opt ')' ':' type ';' function_block ';' '''
    p[0] = [ast.FunctionDecl(p[2], p[4], p[7], p[9])]


def p_function_block(p):
    '''function_block : VAR var_declarations BEGIN optional_statements END
                      | BEGIN optional_statements END'''
    if len(p) == 6:
        p[0] = ast.Block(p[2], p[4])
    else:
        p[0] = ast.Block([], p[2])

def p_param_list_opt(p):
    '''param_list_opt : param_list
                      | empty'''
    p[0] = p[1] if p[1] else []

def p_param_list(p):
    '''param_list : param_list ',' param
                  | param'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_param(p):
    '''param : ID ':' type'''
    p[0] = (p[1], p[3])

def p_id_list(p):
    '''id_list : ID
               | id_list ',' ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_var_declaration(p):
    'var_declaration : id_list ":" type ";"'
    p[0] = [ast.VarDecl(var, p[3]) for var in p[1]]

def p_type(p):
    '''type : INTEGER
            | BOOLEAN
            | STRING_TYPE
            | ARRAY LBRACKET NUMBER DOTDOT NUMBER RBRACKET OF type'''
    if len(p) == 2:
        if p[1] == 'string':
            p[0] = 'string'
        else:
            p[0] = p[1].lower()  # 'integer' ou 'boolean'
    else:
        base_type = p[8] if isinstance(p[8], (str, ast.ArrayType)) else p[8].lower()
        p[0] = ast.ArrayType(int(p[3]), int(p[5]), base_type)





def p_statements(p):
    '''statements : statements statement ';'
                  | statements statement
                  | statement ';'
                  | statement'''
    stmts = []

    for i in range(1, len(p)):
        if isinstance(p[i], list):
            stmts.extend(p[i])
        elif p[i] is not None and not isinstance(p[i], str):
            stmts.append(p[i])
    
    p[0] = stmts


def p_statement(p):
    '''statement : assignment
                 | if_statement
                 | while_loop
                 | for_loop
                 | compound_statement
                 | writeln
                 | write
                 | readln
                 | empty'''
    p[0] = p[1]

def p_assignment(p):
    'assignment : variable ASSIGN expression'
    p[0] = ast.Assignment(p[1], p[3])


def p_if_statement(p):
    '''if_statement : IF expression THEN statement ELSE statement
                    | IF expression THEN statement'''
    if len(p) == 5:
        p[0] = ast.If(p[2], p[4])
    else:
        p[0] = ast.If(p[2], p[4], p[6])

def p_variable_id(p):
    'variable : ID'
    p[0] = ast.Var(p[1])

def p_variable_array_access(p):
    'variable : variable LBRACKET expression RBRACKET'
    p[0] = ast.ArrayAccess(p[1], p[3])


def p_while_loop(p):
    'while_loop : WHILE expression DO statement'
    p[0] = ast.While(p[2], p[4])

def p_for_loop(p):
    '''for_loop : FOR ID ASSIGN expression TO expression DO statement
                | FOR ID ASSIGN expression DOWNTO expression DO statement'''
    downto = (p[5].upper() == 'DOWNTO')
    p[0] = ast.For(p[2], p[4], p[6], p[8], downto=downto)

def p_compound_statement(p):
    'compound_statement : BEGIN statements END'
    p[0] = ast.Compound(p[2])

def p_expression_string(p):
    'expression : STRING'
    p[0] = ast.Const(p[1])  # Cria um nó Const com o valor da string

def p_statement_writeln(p):
    '''writeln : WRITELN "(" expression_list ")" '''
    p[0] = ast.WriteLn(p[3])

def p_statement_write(p):
    '''write : WRITE "(" expression_list ")" '''
    p[0] = ast.Write(p[3])  # ← precisas ter um nó Write definido

def p_statement_readln(p):
    '''readln : READLN "(" expression_list ")" '''
    p[0] = ast.ReadLn(p[3])  # Cria um nó ReadLn com a lista de expressões

def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression
                  | expression DIV expression
                  | expression MOD expression
                  | expression AND expression
                  | expression OR expression
                  | expression '=' expression
                  | expression '<' expression
                  | expression '>' expression
                  | expression LE expression
                  | expression GE expression
                  | expression NE expression'''
    p[0] = ast.BinaryOp(p[2], p[1], p[3])

def p_expression_not(p):
    'expression : NOT expression'
    p[0] = ast.UnaryOp(p[1], p[2])

def p_expression_group(p):
    'expression : "(" expression ")"'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = ast.Const(p[1])

def p_expression_boolean(p):
    '''expression : TRUE
                  | FALSE'''
    value = True if p[1].lower() == 'true' else False
    p[0] = ast.Const(value)

def p_expression_array_access(p):
    'expression : ID LBRACKET expression RBRACKET'
    p[0] = ast.ArrayAccess(ast.Var(p[1]), p[3])

def p_expression_variable(p):
    'expression : variable'
    p[0] = p[1]

def p_expression_id(p):
    'expression : ID'
    p[0] = ast.Var(p[1])

def p_expression_list(p):
    '''expression_list : expression
                       | expression_list "," expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_expression_function_call(p):
    'expression : ID "(" expression_list_opt ")"'
    p[0] = ast.FunctionCall(p[1], p[3] if p[3] is not None else [])

def p_expression_list_opt(p):
    '''expression_list_opt : expression_list
                           | empty'''
    p[0] = p[1]

def p_empty(p):
    'empty :'
    p[0] = None

def p_error(p):
    if p:
        print(f"Erro de sintaxe na linha {p.lineno}: Token inesperado '{p.value}'")
    else:
        print("Erro de sintaxe: Fim de ficheiro inesperado")

parser = yacc.yacc()

if len(sys.argv) < 2:
    print("Uso: python parser.py <ficheiro_pascal.pas>")
    sys.exit(1)

with open(sys.argv[1], encoding="utf-8") as f:
    code = f.read()

result = parser.parse(code)

# Se quiseres imprimir a AST para debugging:
# import pprint; pprint.pprint(result.__dict__, indent=2)

def parse(source_code):
    return parser.parse(source_code)
 