import sys

class Quad():
    def __init__(self, lista):
        self.num = lista[0]
        self.op = lista[1]
        self.arg1 = lista[2]
        self.arg2 = lista[3]
        self.destino = lista[4]

# CARGADOR (LOADER)
try:
    with open("codigo_fuente.obj", "r") as f:
        contenido = f.read()
except FileNotFoundError:
    print("Error: No se encontró 'codigo_fuente.obj'.")
    sys.exit()

# MEMORIA
# Rangos de memoria:  
# Globales: 1000-6999, Constantes: 17000+
# Locales: 7000-11999, Temporales: 12000-16999

mem_global = {}  # Aqui van Globales y Constantes
stack_memoria = [{}] # Pila de diccionarios para Locales y Temporales 

quads = {}
lineas = contenido.split("\n")
seccion = 0 
pila_ejecucion = [] # Para guardar el Instruction Pointer (IP) en llamadas
params_pendientes = [] # Buffer temporal para pasar parametros

for i in lineas:
    linea = i.split()
    if len(linea) == 0:
        seccion += 1
        continue
        
    if seccion == 0: # Constantes
        dir_const = int(linea[-1])
        val_str = " ".join(linea[:-1]) 
        
        if val_str.isdigit(): 
            val_final = int(val_str)
        elif val_str.replace('.', '', 1).isdigit() and val_str.count('.') < 2: 
            val_final = float(val_str)
        else: 
            val_final = val_str.replace('"', '') 
            
        mem_global[dir_const] = val_final
        
    elif seccion == 1: # Contadores 
        pass
        
    elif seccion == 2: # Quads
        idx = int(linea[0])
        quads[idx] = Quad(linea)

# HELPER: GESTION DE MEMORIA
def get_val(addr):
    """Obtiene valor de memoria global o local con validación de inicialización"""
    try:
        addr = int(addr)
    except:
        return None # Si es '_' o error de formato

    val = None

    # BUSQUEDA EN RANGO GLOBAL (1000-6999) O CONSTANTE (>17000)
    if (1000 <= addr < 7000) or (addr >= 17000):
        val = mem_global.get(addr, None)
        
    # BUSQUEDA EN RANGO LOCAL (7000-11999) O TEMPORAL (12000-16999)
    elif 7000 <= addr < 17000:
        # Usamos [-1] para acceder siempre al contexto actual (tope de la pila)
        if stack_memoria:
            val = stack_memoria[-1].get(addr, None)
        else:
            print("Error Fatal: Pila de memoria vacía al intentar leer.")
            sys.exit()
    
    else:
        print(f"Error: Dirección {addr} fuera de rango conocido")
        sys.exit()

    # VALIDACION DE INICIALIZACION (Runtime Error)
    if val is None:
        print(f"\nError de Ejecución: Se intentó usar la variable en dir '{addr}' pero no tiene valor.")
        sys.exit()
        
    return val

def set_val(addr, val):
    """Escribe valor en memoria global o local según el rango"""
    try:
        addr = int(addr)
    except:
        return # Si es -1 o '_'

    # RANGO GLOBAL
    if 1000 <= addr < 7000:
        mem_global[addr] = val
    # RANGO LOCAL O TEMPORAL
    elif 7000 <= addr < 17000:
        stack_memoria[-1][addr] = val
    else:
        print(f"Error: Intento de escritura en dirección inválida {addr}")
        sys.exit()

# EJECUTOR (CPU)
print("\nINICIANDO EJECUCION \n")
ip = 1 

while ip in quads:
    q = quads[ip]
    op = q.op
    
    # Pre cargamos valores para operaciones aritmeticas/logicas
    val1 = get_val(q.arg1) if str(q.arg1) not in ['_', '-1'] else None
    val2 = get_val(q.arg2) if str(q.arg2) not in ['_', '-1'] else None
    dir_res = q.destino # Mantenemos la direccion como string o int para set_val

    if op == 'END':
        print("\nFIN DEL PROGRAMA")
        sys.exit()

    # Aritmetica
    elif op == '+': set_val(dir_res, val1 + val2)
    elif op == '-': set_val(dir_res, val1 - val2)
    elif op == '*': set_val(dir_res, val1 * val2)
    elif op == '/':
        if val2 == 0: print("Error: Division por cero"); sys.exit()
        set_val(dir_res, val1 / val2)
    elif op == '=': 
        # Asignacion directa
        set_val(dir_res, val1)

    # Comparaciones
    elif op == '>': set_val(dir_res, val1 > val2)
    elif op == '<': set_val(dir_res, val1 < val2)
    elif op == '>=': set_val(dir_res, val1 >= val2)
    elif op == '<=': set_val(dir_res, val1 <= val2)
    elif op == '==': set_val(dir_res, val1 == val2)
    elif op == '!=': set_val(dir_res, val1 != val2)

    # Saltos
    elif op == 'GOTO':
        ip = int(q.destino)
        continue 
    elif op == 'GOTOF':
        if not val1:
            ip = int(q.destino)
            continue 
    elif op == 'GOTOT':
        if val1: 
            ip = int(q.destino)
            continue 

    # Funciones 
    elif op == 'ERA':
        params_pendientes = []
        
    elif op == 'PARAM':
        params_pendientes.append((int(q.destino), val1))
        
    elif op == 'GOSUB':
        pila_ejecucion.append(ip + 1) # Guardar a donde regresar
        
        # CREAR NUEVO CONTEXTO
        nuevo_contexto = {}
        
        # CARGAR PARAMETROS EN ESE NUEVO CONTEXTO
        # Como los parametros son locales (7000+), se guardan en el nuevo dict
        for par_dir, par_val in params_pendientes:
            nuevo_contexto[par_dir] = par_val
            
        # PUSHEAR AL STACK DE MEMORIA
        stack_memoria.append(nuevo_contexto)
        
        # Limpiar buffer y saltar
        params_pendientes = [] 
        ip = int(q.destino)
        continue
        
    elif op == 'ENDFUNC':
        # Destruir variables locales
        stack_memoria.pop()
        
        # REGRESAR AL IP ANTERIOR
        ip = pila_ejecucion.pop()
        continue

    # Print
    elif op == 'PRINT':
        val_print = get_val(q.destino)
        print(val_print, end='')
        
    elif op == 'PRINTN':
        print("")
        
    ip += 1