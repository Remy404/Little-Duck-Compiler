import ply.lex as lex    # importa lex

reserved = {
    'program': 'PROGRAM',
    'var':     'VAR',
    'int':     'INT',
    'float':   'FLOAT',
    'string':  'STRING',
    'void':    'VOID', 
    'if':      'IF',
    'else':    'ELSE',   
    'while':   'WHILE',
    'do':      'DO',
    'print':   'PRINT',   
    'end':     'END',
    'main':    'MAIN',
}

# Lista de tokens
tokens = [
    'CONST_INT', 'CONST_FLOAT', 'CONST_STRING', 'IDENTIFIER',
    'OP_ASIGNA', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LT', 'LE', 'GT','GE',
    'EQ', 'NE', 'SEMICOL', 'COLON', 'COMMA', 'LPAREN','RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET'
] + list(reserved.values())

# Tokens
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_OP_ASIGNA = r'='
t_LE        = r'<='
t_LT        = r'<'
t_GE        = r'>='
t_GT        = r'>'
t_EQ        = r'=='
t_NE        = r'!='
t_SEMICOL   = r';'
t_COLON     = r':'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'

def t_CONST_FLOAT(t):
    r'([0-9]+\.[0-9]*|\.[0-9]+)([eE][+-]?[0-9]+)?'
    t.value = float(t.value)
    return t

def t_CONST_INT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_CONST_STRING(t):
    r'"([^"\\]|\\.)*"'
    raw = t.value[1:-1]
    try:
        t.value = bytes(raw, "utf-8").decode("unicode_escape")
    except Exception:
        t.value = raw
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_COMMENT(t):
    r'\#[^\n]*'
    t.value = t.value.lstrip()
    pass

def t_COMMA(t):
    r'\,'
    t.type = 'COMMA'
    return t

t_ignore  = ' \t\r'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

archivo = "programa.txt"
try:
    with open(archivo, "r", encoding="utf-8") as f:
        input_program = f.read()
except FileNotFoundError:
    print(f"No se encontró el archivo '{archivo}'")
    exit() 

# Build the lexer  
lexer = lex.lex()
lexer.input(input_program)