import ply.yacc as yacc
from Little_duck_lexer import tokens, lexer
import sys

# GESTOR DE MEMORIA
class MemoryManager:
    def __init__(self):
        # Direcciones base
        self.bases = {
            'global': {'int': 1000, 'float': 2000, 'string': 3000},
            'local':  {'int': 7000, 'float': 8000, 'string': 9000},
            'temp':   {'int': 12000, 'float': 13000, 'bool': 14000},
            'const':  {'int': 17000, 'float': 18000, 'string': 19000}
        }
        # Contadores 
        self.counters = {
            'global': {'int': 0, 'float': 0, 'string': 0},
            'local':  {'int': 0, 'float': 0, 'string': 0},
            'temp':   {'int': 0, 'float': 0, 'bool': 0},
            'const':  {'int': 0, 'float': 0, 'string': 0}
        }

    def get_address(self, scope, type_v):
        if type_v not in self.bases[scope]: return -1 # Error safety
        address = self.bases[scope][type_v] + self.counters[scope][type_v]
        self.counters[scope][type_v] += 1
        return address
    
    def reset_local(self):
        # Reiniciamos contadores locales y temporales
        self.counters['local'] = {'int': 0, 'float': 0, 'string': 0}
        self.counters['temp']  = {'int': 0, 'float': 0, 'bool': 0}

# ESTRUCTURA DE DATOS
class CompilerData:
    def __init__(self):
        self.dir_func = {'global': {'vars': {}}} 

        self.stack_operands = []  # (operand, type)
        self.stack_operators = [] # (+, -, *, ...)
        self.stack_jumps = [] # (quad_index)

        self.quad_list = []
        self.quad_counter = 1

        self.current_scope = 'global'
        self.vars_pending = []        
        self.avail_temp = 0

        self.call_stack = []  # Pila para manejar llamadas anidadas: [(func_name, param_counter)]
        
        # INTEGRACION MEMORIA
        self.memory = MemoryManager()
        self.constants = {} # { valor_real : {'addr': 17000, 'type': 'int'} }

data = CompilerData()

# Cubo semantico
semantic_cube = {
    #PLUS 
    ('int', 'int', '+'): 'int', ('float', 'float', '+'): 'float', 
    ('string', 'string', '+'): 'string', ('int', 'float', '+'): 'float', 
    ('float', 'int', '+'): 'float',

    #MINUS
    ('int', 'int', '-'): 'int', ('int', 'float', '-'): 'float',
    ('float', 'int', '-'): 'float', ('float', 'float', '-'): 'float', 
    
    #TIMES
    ('int', 'int', '*'): 'int', ('int', 'float', '*'): 'float',
    ('float', 'int', '*'): 'float', ('float', 'float', '*'): 'float',
    
    #DIVIDE
    ('int', 'int', '/'): 'float', ('int', 'float', '/'): 'float',
    ('float', 'int', '/'): 'float', ('float', 'float', '/'): 'float',

    #COMP_OPS
    ('int', 'int', '>'): 'bool', ('int', 'float', '>'): 'bool',
    ('float', 'float', '>'): 'bool',('float', 'int', '>'): 'bool',
    ('int', 'int', '<'): 'bool', ('int', 'float', '<'): 'bool',
    ('float', 'float', '<'): 'bool',('float', 'int', '<'): 'bool',
    ('int', 'int', '>='): 'bool', ('int', 'float', '>='): 'bool',
    ('float', 'float', '>='): 'bool',('float', 'int', '>='): 'bool',
    ('int', 'int', '<='): 'bool', ('int', 'float', '<='): 'bool',
    ('float', 'float', '<='): 'bool',('float', 'int', '<='): 'bool',

    #ASIGNA
    ('int', 'int', '='): 'ok',('float', 'float', '='): 'ok',
    ('float', 'int', '='): 'ok',('int', 'float', '='): 'ok',
    ('string', 'string', '='): 'ok',

    #EQUALS / NOT EQUALS
    ('int', 'int', '=='): 'bool', ('int', 'int', '!='): 'bool',
    ('float', 'float', '=='): 'bool', ('float', 'float', '!='): 'bool',
    ('string', 'string', '=='): 'bool', ('string', 'string', '!='): 'bool',
    ('int', 'float', '=='): 'bool',('float', 'int', '=='): 'bool',
    ('int', 'float', '!='): 'bool',('float', 'int', '!='): 'bool',
}

def generate_quad(op, left, right, res):
    quad = [data.quad_counter, op, left, right, res]
    data.quad_list.append(quad)
    data.quad_counter += 1

def get_var_type(var_name):
    # Buscamos en scope local
    if data.current_scope != 'global':
        if var_name in data.dir_func[data.current_scope]['vars']:
            return data.dir_func[data.current_scope]['vars'][var_name]['type']
    # Buscamos en scope global
    if var_name in data.dir_func['global']['vars']:
        return data.dir_func['global']['vars'][var_name]['type']
    return 'error'

def solve_quad():
    if len(data.stack_operators) > 0:
        right_addr, right_type = data.stack_operands.pop()
        left_addr, left_type = data.stack_operands.pop()
        operator = data.stack_operators.pop()
        
        res_type = semantic_cube.get((left_type, right_type, operator), 'error')
        
        if res_type != 'error':
            # SOLICITAR DIRECCION TEMPORAL
            temp_addr = data.memory.get_address('temp', res_type)
            generate_quad(operator, left_addr, right_addr, temp_addr)
            data.stack_operands.append((temp_addr, res_type))
        else:
            print(f"Error Semantico Type Mismatch: {left_type} {operator} {right_type}")
            sys.exit()

# REGLA 1: PROGRAMA
def p_programa(t):
    '''programa : PROGRAM IDENTIFIER SEMICOL vars_opt funcs_opt MAIN np_main body END'''
    print("\n--- COMPILACION EXITOSA---")
    print("--- Cuadruplos Generados ---")
    generate_quad('END', -1, -1, -1)
    for q in data.quad_list:
        print(f"{q[0]}: {q[1]} {q[2]} {q[3]} {q[4]}")

def p_np_main(t):
    '''np_main : '''
    # Rellenar el GOTO inicial para saltar al main
    data.quad_list[0][4] = data.quad_counter

# Inicializacion del programa (GOTO main)
generate_quad('GOTO', '_', '_', 'pending') # Quad 1 salto al main

def p_funcs_opt(t):
    '''funcs_opt : funcs_cycle'''
    
def p_funcs_cycle(t):
    '''funcs_cycle : funcs funcs_cycle
                   | empty'''

def p_vars_opt(t):
    '''vars_opt : vars
                | empty'''

#FUNCIONES
#Aqui tuvimos que dividir la regla en dos partes. Esto fue necesario para detectar el inicio de la funcion y cambiar 
#el contexto (scope)inmediatamente, asegurandonos que las variables que sigan guardando como locales 
#y no se mezclen con las globales.

def p_func_header(t):
    '''func_header : VOID IDENTIFIER'''
    func_name = t[2]
    if func_name in data.dir_func:
        print(f"Error: Funcion '{func_name}' ya declarada.")
        sys.exit()
    else:
        data.dir_func[func_name] = {
            'type': 'void',
            'vars': {},
            'params': [], # Lista de tipos (int, float...)
            'param_addresses': [], # Direcciones de los parametros
            'start_quad': data.quad_counter 
        }
        data.current_scope = func_name 

def p_funcs(t):
    '''funcs : func_header LPAREN id_colon_type_opt RPAREN LBRACKET vars_opt body RBRACKET SEMICOL'''
    # Generar EndFunc
    generate_quad('ENDFUNC', '_', '_', '_')
    data.memory.reset_local()
    data.current_scope = 'global'

def p_id_colon_type_opt(t):
    '''id_colon_type_opt : id_colon_type id_colon_type_comma_cycle
                           | empty'''
    
def p_id_colon_type_comma_cycle(t):
    '''id_colon_type_comma_cycle : COMMA id_colon_type id_colon_type_comma_cycle
                                   | empty'''

def p_id_colon_type(t):
    '''id_colon_type : IDENTIFIER COLON type'''
    var_name = t[1]
    var_type = t[3]
    
    if var_name in data.dir_func[data.current_scope]['vars']:
        print(f"Error: Parametro '{var_name}' ya declarado.")
        sys.exit()
    else:
        # Pedir direccion local
        addr = data.memory.get_address('local', var_type)
        
        # Guardar en vars con su direccion real
        data.dir_func[data.current_scope]['vars'][var_name] = {'type': var_type, 'dir': addr}
        
        # Guardar en listas de parametros
        data.dir_func[data.current_scope]['params'].append(var_type)
        if 'param_addresses' in data.dir_func[data.current_scope]:
             data.dir_func[data.current_scope]['param_addresses'].append(addr)

# VARS
def p_vars(t):
    '''vars : VAR p_vars_list'''

def p_vars_list(t):
    '''p_vars_list : p_vars_item p_vars_list 
                   | empty'''

def p_vars_item(t):
    '''p_vars_item : id_cycle COLON type SEMICOL
                   | error SEMICOL''' 
    
    if len(t) > 3: 
        current_type = t[3]
        scope_type = 'global' if data.current_scope == 'global' else 'local'

        for var_name in data.vars_pending:
            if var_name in data.dir_func[data.current_scope]['vars']:
                print(f"Error: Variable '{var_name}' ya declarada en {data.current_scope}")
            else:
                addr = data.memory.get_address(scope_type, current_type)
                # Guardamos la direccion
                data.dir_func[data.current_scope]['vars'][var_name] = {'type': current_type, 'dir': addr}
                print(f"Var '{var_name}' vinculada a dir {addr} ({scope_type})")
                
        data.vars_pending = []

def p_id_cycle(t): 
    '''id_cycle : IDENTIFIER id_cycle_comma'''
    data.vars_pending.insert(0, t[1]) 

def p_id_cycle_comma(t):
    '''id_cycle_comma : COMMA IDENTIFIER id_cycle_comma 
                      | empty'''
    if len(t) > 2: data.vars_pending.append(t[2])

def p_type(t):
    '''type : INT
            | FLOAT
            | STRING'''
    t[0] = t[1]

def p_body(t):
    '''body : LBRACE statement_list RBRACE'''

# STATEMENT
def p_statement_list(t):
    '''statement_list : statement statement_list 
                      | empty'''

def p_statement(t):
    '''statement : asigna 
                 | condition 
                 | cycle
                 | print_st
                 | f_call'''

# ASIGNACION
def p_asigna(t):
    "asigna : IDENTIFIER OP_ASIGNA expresion SEMICOL"
    var_name = t[1]
    
    var_info = None

    # BUSCA EN LOCAL (Si no estamos en scope global)
    if data.current_scope != 'global':
        if var_name in data.dir_func[data.current_scope]['vars']:
            var_info = data.dir_func[data.current_scope]['vars'][var_name]

    # BUSCA EN GLOBAL (Si no se encontró en local)
    if var_info is None and var_name in data.dir_func['global']['vars']:
        var_info = data.dir_func['global']['vars'][var_name]

    # VERIFICA SI EXISTE
    if var_info is None:
        print(f"Error: Variable '{var_name}' no existe en este contexto.")
        sys.exit()
        
    # Extraer datos reales
    var_addr = var_info['dir']
    var_type = var_info['type']
    
    # Sacar valor de la pila
    val_addr, val_type = data.stack_operands.pop()
    
    # Validar tipos
    res_type = semantic_cube.get((var_type, val_type, '='), 'error')
    if res_type == 'error':
        print(f"Error: No se puede asignar {val_type} a {var_name} ({var_type})")
        sys.exit()

    # Generar Quad con direcciones
    generate_quad('=', val_addr, -1, var_addr)

def p_condition(t):
    '''condition : IF LPAREN expresion RPAREN np_if_1 body else_opt SEMICOL'''
    # AL FINAL DEL IF: Sacamos el salto pendiente (del Falso o del Else) y lo rellenamos
    end_jump = data.stack_jumps.pop()
    data.quad_list[end_jump-1][4] = data.quad_counter

def p_np_if_1(t):
    '''np_if_1 : '''
    cond_addr, cond_type = data.stack_operands.pop()
    if cond_type != 'bool':
        print("Error: If espera un booleano")
        sys.exit()
        
    # Generamos GOTOF con destino pendiente (-1)
    generate_quad('GOTOF', cond_addr, -1, -1) 
    # Guardamos el índice de este quad para rellenarlo luego
    data.stack_jumps.append(data.quad_counter - 1) # -1 porque el counter ya avanzó

def p_else_opt(t):
    '''else_opt : ELSE np_else body
                | empty'''

def p_np_else(t):
    '''np_else : '''
    # Generar GOTO para que la parte TRUE se salte la parte FALSE
    generate_quad('GOTO', -1, -1, -1)
    
    # El GOTOF original (del if) debe venir aqui
    false_jump = data.stack_jumps.pop()
    data.quad_list[false_jump-1][4] = data.quad_counter
    
    # Metemos el nuevo GOTO a la pila para rellenarlo al final
    data.stack_jumps.append(data.quad_counter - 1)

# DO-WHILE
def p_cycle(t):
    '''cycle : DO np_do body WHILE LPAREN expresion RPAREN SEMICOL np_do_check'''

def p_np_do(t):
    '''np_do : '''
    # Guardamos checkpoint de retorno 
    data.stack_jumps.append(data.quad_counter)

def p_np_do_check(t):
    '''np_do_check : '''
    cond_addr, cond_type = data.stack_operands.pop()
    
    if cond_type != 'bool':
        print("Error: Do-While requiere booleano")
        sys.exit()
    
    return_jump = data.stack_jumps.pop()
    
    # DO-WHILE usa GOTOT (Si es VERDADERO, regresa al inicio)
    generate_quad('GOTOT', cond_addr, -1, return_jump)

# PRINT
def p_print_st(t):
    '''print_st : PRINT LPAREN print_list RPAREN SEMICOL'''
    generate_quad('PRINTN', -1, -1, -1)

def p_print_list(t):
    '''print_list : expresion np_print print_list_prime'''

def p_print_list_prime(t):
    '''print_list_prime : COMMA expresion np_print print_list_prime
                        | empty'''

def p_np_print(t):
    '''np_print : '''
    if len(data.stack_operands) > 0:
        val_addr, _ = data.stack_operands.pop()
        generate_quad('PRINT', -1, -1, val_addr)
    else:
        print("Error: Pila de operandos vacia al intentar imprimir")
        sys.exit()

def p_f_call(t):
    '''f_call : IDENTIFIER np_verify_func LPAREN f_call_args_opt RPAREN np_gen_gosub SEMICOL'''

def p_np_verify_func(t):
    '''np_verify_func : '''
    func_name = t[-1] 
    if func_name not in data.dir_func:
        print(f"Error: Funcion '{func_name}' no declarada.")
        sys.exit()
    
    # Generamos ERA con la dirección de inicio de la función
    generate_quad('ERA', -1, -1, func_name)
    
    # Iniciar stack de llamadas
    data.call_stack.append({'name': func_name, 'k': 0})

def p_f_call_args_opt(t):
    '''f_call_args_opt : f_call_args_list
                       | empty'''

def p_f_call_args_list(t):
    '''f_call_args_list : expresion np_param_check f_call_args_list_prime'''

def p_f_call_args_list_prime(t):
    '''f_call_args_list_prime : COMMA expresion np_param_check f_call_args_list_prime
                              | empty'''

def p_np_param_check(t):
    '''np_param_check : '''
    arg_addr, arg_type = data.stack_operands.pop()
    
    call_info = data.call_stack[-1]
    func_name = call_info['name']
    k = call_info['k']
    
    # Validaciones
    params_list = data.dir_func[func_name]['params']
    if k >= len(params_list):
        print(f"Error: Demasiados argumentos")
        sys.exit()
    
    param_type = params_list[k]
    if arg_type != param_type:
        print(f"Error: Tipo incorrecto. Esperaba {param_type}")
        sys.exit()
        
    # Recuperamos la direccion
    target_addr = data.dir_func[func_name]['param_addresses'][k]
    
    # Generamos el quad enviando el valor a esa direccion
    generate_quad('PARAM', arg_addr, -1, target_addr)
    
    data.call_stack[-1]['k'] += 1

def p_np_gen_gosub(t):
    '''np_gen_gosub : '''
    call_info = data.call_stack.pop()
    func_name = call_info['name']
    k = call_info['k']
    
    # Validar si faltaron params
    total_params = len(data.dir_func[func_name]['params'])
    if k < total_params:
        print(f"Error: Faltan argumentos para '{func_name}'.")
        sys.exit()
        
    start_quad = data.dir_func[func_name]['start_quad']
    generate_quad('GOSUB', -1, -1, start_quad)


#  EXPRESION
def p_expresion(t):
    '''expresion : exp np_gen_rel
                 | exp'''

def p_np_gen_rel(t):
    '''np_gen_rel : GT exp
                  | LT exp
                  | EQ exp
                  | NE exp
                  | GE exp
                  | LE exp'''

    operator = t[1]
    right_addr, right_type = data.stack_operands.pop()
    left_addr, left_type = data.stack_operands.pop()
    
    # Valida en cubo
    res_type = semantic_cube.get((left_type, right_type, operator), 'error')
    if res_type == 'error':
        print("Error de tipos en comparación")
        sys.exit()
        
    temp_addr = data.memory.get_address('temp', res_type)
    generate_quad(operator, left_addr, right_addr, temp_addr)
    data.stack_operands.append((temp_addr, res_type))

# EXP 
def p_exp(t):
    '''exp : term np_gen_add
           | exp PLUS np_push_plus term np_gen_add
           | exp MINUS np_push_minus term np_gen_add'''

# TERMINO 
def p_term(t):
    '''term : factor np_gen_mul
            | term TIMES np_push_times factor np_gen_mul
            | term DIVIDE np_push_divide factor np_gen_mul'''
    
# PUNTOS NEURALGICOS
def p_np_push_plus(t):
    '''np_push_plus : '''
    data.stack_operators.append('+')

def p_np_gen_add(t):
    '''np_gen_add : '''
    if len(data.stack_operators) > 0:
        if data.stack_operators[-1] in ['+', '-']: 
            solve_quad()

def p_np_push_minus(t):
    '''np_push_minus : '''
    data.stack_operators.append('-')

def p_np_push_times(t):
    '''np_push_times : '''
    data.stack_operators.append('*')

def p_np_push_divide(t):
    '''np_push_divide : '''
    data.stack_operators.append('/')

def p_np_gen_mul(t):
    '''np_gen_mul : '''
    if len(data.stack_operators) > 0:
        if data.stack_operators[-1] in ['*', '/']:
            solve_quad()

# FACTOR
def p_factor(t):
    '''factor : LPAREN np_paren_open expresion RPAREN np_paren_close
              | factor_const
              | factor_id'''

def p_np_paren_open(t):
    '''np_paren_open : '''
    pass

def p_np_paren_close(t):
    '''np_paren_close : '''
    pass

def p_factor_id(t):
    "factor_id : IDENTIFIER"
    var_name = t[1]
    var_info = None
    # Primero buscamos en Local, si no estamos en global
    if data.current_scope != 'global':
        if var_name in data.dir_func[data.current_scope]['vars']:
            var_info = data.dir_func[data.current_scope]['vars'][var_name]
    # SI NO ENCONTRAMOS, buscamos en Global
    if var_info is None and var_name in data.dir_func['global']['vars']:
        var_info = data.dir_func['global']['vars'][var_name]

    # Validamos
    if var_info:
        data.stack_operands.append((var_info['dir'], var_info['type']))
    else:
        print(f"Error: Variable '{var_name}' no declarada.")
        sys.exit()

def p_factor_const(t):
    """factor_const : CONST_INT 
                    | CONST_FLOAT
                    | CONST_STRING"""
    val = t[1]
    v_type = 'int' if isinstance(val, int) else 'float'
    
    # REVISAR SI LA CONSTANTE YA EXISTE
    if isinstance(val, int): 
        v_type = 'int'
    elif isinstance(val, float): 
        v_type = 'float'
    else: 
        v_type = 'string'
    
    if val not in data.constants:
        addr = data.memory.get_address('const', v_type)
        data.constants[val] = {'addr': addr, 'type': v_type}
        print(f"Constante '{val}' asignada a dir {addr}")
    
    # PUSH DIRECCION CONSTANTE A LA PILA
    addr = data.constants[val]['addr']
    data.stack_operands.append((addr, v_type))

def p_empty(t): 'empty :'
def p_error(t): print(f"Error sintaxis {t.value} en linea {t.lineno}")

# EJECUCION

archivo = "programa.txt"
try:
    with open(archivo, "r", encoding="utf-8") as f:
        input_program = f.read()
except FileNotFoundError:
    print(f"No se encontro el archivo '{archivo}'")
    exit() 

parser = yacc.yacc()
result = parser.parse(input_program)

# Escribir archivo para VM
with open("codigo_fuente.obj", "w") as f:
    # Constantes
    for val, info in data.constants.items():
        f.write(f"{val} {info['addr']}\n")
    f.write("\n") # linea vacia separadora
    
    # Contadores
    f.write("global_int 5\n") 
    f.write("\n") # linea vacia separadora
    
    # Quads
    for q in data.quad_list:
        f.write(f"{q[0]} {q[1]} {q[2]} {q[3]} {q[4]}\n")

print("\nArchivo 'codigo_fuente.obj' generado.")





