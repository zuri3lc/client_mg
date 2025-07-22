#Modulo encargado de todo lo que ve el usuario
# ---------- IMPORTS -----------
from decimal import (
    Decimal,
    InvalidOperation
    )
from .database import (
    get_username_by_id_db
    )
from .utils import (
    clean_input
)

# ----- FUNCION PARA EL MENU -----
def mostrar_menu_principal(usuario_sistema_id):
    nombre_usuario = get_username_by_id_db(usuario_sistema_id) #obtenemos el nombre del usuario actual   
    print(f"\n| HOLA {nombre_usuario}, Que deseas hacer?\n")
    print("| MENU DEL GESTOR DE CLIENTES\n")
    print("| 1. Agregar nuevo cliente")
    print("| 2. Actualizar Saldo")
    print("| 3. Modificar cliente existente")
    print("| 4. Buscar clientes")
    print("| 5. Obtener todos los clientes")
    print("| 6. Eliminar cliente")
    print("| 7. Ver historial de movimientos")
    print("| 8. Cerrar Sesion")
    print('-' * 40)

# --- IMPRIME LOS CLIENTES FORMATEADOS ----
def mostrar_clientes(clientes):
    total_saldo = Decimal(0) #inicializamos el total del saldo en 0
    for row in clientes: #type: ignore
        id_cliente = row[0]
        nombre = row[1]
        telefono = row[2]
        comentario = row[5]
        ultima_modificacion = row[7].srftime("%d/%m/%Y")
        saldo = row[8]
        estado = row[9]
        
        print(f"\nID: {id_cliente}")
        print(f"Nombre: {nombre}")
        print(f"Telefono: {telefono or 'N/A'}")
        print(f"Comentario: {comentario or 'N/A'}")
        print(f"Ultima modificacion: {ultima_modificacion}")
        print(f"Saldo: {saldo}")
        print(f"Estado: {estado}")
        print("=" * 80)
        
        total_saldo += saldo

    print(f"\n--- Total de clientes: {len(clientes)} ---") #type: ignore
    print(f"--- Saldo Global: ${total_saldo} ---\n")

# ---- MUESTRA EL HISTORIAL ---
def mostrar_historial_movimientos(movimientos):
    nombre_cliente = movimientos[0][6]
    client_id = movimientos[0][0]
    print("\n" + "=" * 85)
    print(f"\n=== HISTORIAL DE MOVIMIENTOS PARA {nombre_cliente.upper()} ===\n")
    print("=" * 85)
    print(f"{'Fecha':<12} | {'Tipo':<15} | {'Monto':>12} | {'Saldo Anterior':>15} | {'Saldo Final':>15}")
    print("=" * 85)
        
    for fila in movimientos: # iteramos en cada fila obtenuida de historial_movimientos 
        fecha = fila[1].strftime("%d/%m/%y")
        tipo = fila[2].replace('_', ' ').title()
        monto = fila[3]
        saldo_anterior = fila[4]
        saldo_final = fila[5]
        
        print(f"{fecha:<12} | {tipo:<15} | ${monto:>11.2f} | {saldo_anterior:>14.2f} | {saldo_final:>14.2f}")
        print("=" * 85)

#---- SOLICITA DATOS ----
def solicitar_info_clientes():
    """Solicita la informacion del cliente al usuario.
    Retorna un diccionario con los datos o None si la validacion falla"""

    data = {} #creamos un diccionario vacio para almacenar los datos
    
    #--TELEFONO--
    while True:
        telefono = clean_input(
            "\n| Telefono (10 digitos): (Deje vacio para omitir): \n",
            min_len=0,
            max_len=10,
            allow_empty=True,
            to_none_on_empty=True
        )
        if telefono is None: #si es usuario dejo vacio, se asigna None y salimos
            data['telefono'] = None
            break
        elif telefono.isdigit() and len(telefono) == 10: # si no, validamos si los digitos
            data['telefono'] = telefono # -/- insertamos telefono en el diccionario -/-
            break
        else:
            print(" -ERROR- el telefono debe tener 10 digitos.")
            
    #--SALDO--
    while True:
        saldo_str = clean_input(
            "\n| Saldo Actual (OBLIGATORIO)\n",
            min_len=1,
            max_len=10,
            allow_empty=False,
            to_none_on_empty=False
        )
        if not saldo_str:
            print("\n- ERROR- El saldo es obligatorio, no puede estar vacio\n")
            continue
        try:
            saldo = Decimal(saldo_str)
            if saldo <= 0:
                print("\n -ERROR- El saldo no pued ser menor o igual  a '0' \n")
                continue
            data["saldo_incial"] = saldo #guardamos el saldo
            break
        except InvalidOperation: # Capturamos el error especifico de decimal
            print(f"\n -ERROR- Ingrese un monto numerico valido (ej. 100, 50.50\n")
            continue
        except Exception as e: #capturamos otros errores generales
            print(f"\n -ERROR INESPERADO- Ocurrio un error inesperado al procesar el saldo: {e}\n")
            continue
    
    #--UBICACION--
    data["ubicacion"] = clean_input(
            "\n| Ubicacion aproximada: (Deje vacio para omitir)\n",
            allow_empty=True,
            to_none_on_empty=True
        )
    
    #--FOTO DOMICILIO--
    data["foto_domicilio"] = clean_input(
            "\n| Ingrese la ruta a la foto del Domicilio: (Deje vacio para omitir)\n",
            allow_empty=True,
            to_none_on_empty=True
    )

    #--COMENTARIO--
    data["comentario"] = clean_input(
            "\n| Comentario: (Deje vacio para omitir)\n",
            allow_empty=True,
            to_none_on_empty=True
    )
    
    return data
