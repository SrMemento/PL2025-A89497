import sys
import ply.lex as lex

# -------------------------
# Palavras-chave reservadas
# -------------------------
reserved = {
    'program': 'PROGRAM',
    'begin': 'BEGIN',
    'end': 'END',
    'var': 'VAR',
    'integer': 'INTEGER',
    'boolean': 'BOOLEAN',
    'true': 'TRUE',
    'false': 'FALSE',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'for': 'FOR',
    'to': 'TO',
    'readln': 'READLN',
    'writeln': 'WRITELN',
    'function': 'FUNCTION',
    'procedure': 'PROCEDURE',
    'array': 'ARRAY',
    'of': 'OF',
    'not': 'NOT',
    'and': 'AND',
    'or': 'OR',
    'div': 'DIV',
    'mod': 'MOD',
    'downto': 'DOWNTO',
    'string': 'STRING_TYPE',
    'write': 'WRITE'
}

# -------------------------
# Tokens adicionais
# -------------------------
tokens = [
    'ID',
    'NUMBER',
    'STRING',

    # Operadores compostos
    'ASSIGN',  # :=
    'NE',      # <>
    'LE',      # <=
    'GE',      # >=
    'DOTDOT',   # ..
    'LBRACKET',
    'RBRACKET'
]

tokens += list(reserved.values())

# -------------------------
# Literais (símbolos simples)
# -------------------------
literals = ['+', '-', '*', '/', '(', ')', '=', '<', '>', ':', ';', '.', ',']

# -------------------------
# Regras para operadores compostos
# -------------------------
t_ASSIGN = r':='
t_NE     = r'<>'
t_LE     = r'<='
t_GE     = r'>='
t_DOTDOT = r'\.\.'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'


# -------------------------
# Ignorar espaços e tabulações
# -------------------------
t_ignore = ' \t'

# -------------------------
# Comentários: {}, (* *), // 
# -------------------------
def t_COMMENT(t):
    r'\{[^}]*\}|\(\*([^*]|\*+[^*)])*\*+\)|//.*'
    pass

# -------------------------
# Identificadores e palavras-chave
# -------------------------
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'ID')  # verifica se é palavra-chave
    return t

# -------------------------
# Strings (entre aspas simples)
# -------------------------
def t_STRING(t):
    r'\'([^\\\n]|(\\.))*?\''
    t.value = t.value[1:-1]  # Remove as aspas
    return t


# -------------------------
# Números inteiros
# -------------------------
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# -------------------------
# Contador de linhas
# -------------------------
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# -------------------------
# Tratamento de erro
# -------------------------
def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)

# -------------------------
# Construir o lexer
# -------------------------
lexer = lex.lex()


# -------------------------
# Ler nome do ficheiro
# -------------------------
if len(sys.argv) < 2:
    print("Uso: python lexer.py <ficheiro_pascal.pas>")
    sys.exit(1)

filename = sys.argv[1]

with open(filename, "r", encoding="utf-8") as f:
    code = f.read()

lexer.input(code)

for tok in lexer:
    print(tok)
