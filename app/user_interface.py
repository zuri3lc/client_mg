#Modulo encargado de todo lo que ve el usuario
# ---------- IMPORTS -----------
from decimal import (
    Decimal,
    InvalidOperation
    )
from .database import (
    get_username_by_id_db,
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
    print("| 2. Obtener todos los clientes")
    print("| 3. Actualizar Saldo")
    print("| 4. Modificar cliente existente")
    print("| 5. Buscar clientes")
    print("| 6. Ver historial de movimientos")
    print("| 7. Cambiar estado del cliente")
    print("| 8. Eliminar cliente")
    print("| 9. Cerrar Sesion")
    print('-' * 40)

# --- IMPRIME TODOS LOS CLIENTES FORMATEADOS ----
def mostrar_clientes(clientes):
    total_saldo = Decimal(0) #inicializamos el total del saldo en 0
    for row in clientes: #type: ignore
        id_cliente = row['id']
        nombre = row['nombre']
        telefono = row['telefono']
        comentario = row['comentario']
        ultima_modificacion = row['fecha_ultima_modificacion'].strftime("%d/%m/%Y")
        saldo = row['saldo_actual']
        estado = row['estado_cliente']
        
        print(f"\nID: {id_cliente}")
        print(f"Nombre: {nombre}")
        print(f"Telefono: {telefono or 'N/A'}")
        print(f"Comentario: {comentario or 'N/A'}")
        print(f"Ultima modificacion: {ultima_modificacion}")
        print(f"Saldo: {saldo}")
        print(f"Estado: {estado.upper()}")
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
        
        print(f"{fecha:<12} | {tipo:<15} | ${monto:>11.2f} | ${saldo_anterior:>14.2f} | ${saldo_final:>14.2f}")
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

#---- MUESTRA TODA LA INFORMACION UN SOLO CLIENTE---
def mostrar_cliente_detalle(cliente):
    """Toma la unica fila y la formatea"""
    if not cliente:
        print(f"---ERROR---\nNo se pudieron obtener los datos del cliente...\n")
        return
    # cliente_id, nombre, telefono, ubicacion, foto_domicilio, comentario, fecha_creacion, fecha_mod, saldo, estado = cliente
    cliente_id = cliente['id']
    nombre = cliente['nombre']
    telefono = cliente['telefono']
    ubicacion = cliente['ubicacion_aproximada']
    comentario = cliente['comentario']
    fecha_creacion = cliente['fecha_adquisicion']
    fecha_mod = cliente['fecha_ultima_modificacion'].strftime("%d/%m/%Y")
    saldo = cliente['saldo_actual']
    estado = cliente['estado_cliente']
    
    print(f"\n" + "=" * 50)
    print(f" " * 15, "DETALLES DEL CLIENTE")
    print("=" * 50)
    print(f"| ID: {cliente_id}")
    print(f"| Nombre: {nombre}")
    print(f"| Telefono: {telefono or 'N/A'}")
    print(f"| Ubicacion: {ubicacion or 'N/A'}")
    print(f"| Comentario: {comentario or 'N/A'}")
    print(f"| Fecha de creacion: {fecha_creacion.strftime('%d/%m/%Y')}")
    print(f"| Ultima modificacion: {fecha_mod.strftime('%d/%m/%Y')}")
    print(f"| Saldo: ${saldo:.2f}")
    print(f"| Estado: --{estado.upper()}--")
    print("=" * 50)

#--- SOLICITA EL NOMBRE DEL CLIENTE Y LO VALIDA---
def solicitar_nombre_cliente(validation_func):
    while True:
        nombre = clean_input(
            "| Nombre (OBLIGATORIO): formato 'Nombre Apellido' min 3 caracteres, max 255: \n",
            min_len=3,
            max_len=255,
            allow_empty=False
        ) #clean_input maneja longitud y vacio
        if not nombre:
            continue
        #aqui validamos con la funcion
        if validation_func(nombre):
            return nombre #returnamos el nombre valido
        else:
            print(f"\n----ERROR----\nEl nombre '{nombre}' ya existe  o no es valido \n")
            #reintentamos
            reintentar = input("Desea intentar con otro nombre? (S/N)").strip().upper()
            if reintentar != 'S':
                return None #si no quiere reintentar devolvemos none

#---- SOLICITA LOS DATOS PARA LA ACTUALIZACION -----
def solicitar_datos_actualizacion(cliente_existente, check_name_func):
    """Muestra los datos actualies y solicita nuevos"""
    print("\nINGRESE LOS NUEVOS VALORES PARA LOS CAMPOS A ACTUALIZAR")
    print("(DEJE EN BLANCO PARA OMITIR, ESCRIBA 'NULL' PARA BORRAR VALOR ACTUAL)")
    print("=" * 50)
    updates = {} #creamos un diccionario vacio para almacenar los valores
    cliente_id_actual = cliente_existente[0]
    nombre_actual = cliente_existente[1]
    #Nombre
    #------------------------------------------------------------------
    while True:
        nombre = clean_input(
            f"| Nuevo nombre (actual: {cliente_existente[1]}): formato 'Nombre Apellido' min 3 caracteres, max 255\n",
            min_len=3,
            max_len=255,
            allow_empty=True,
            to_none_on_empty=False,
            special_null_keyword=None
            )
        
        if not nombre:
            print("--- OMITIDO ---\nEl nombre no se modificara\n")
            break
        if nombre.strip().lower() == nombre_actual.strip().lower():
            print("El nombre ingresado es el  mismo que el actual\n---OMITIENDO---\n")
            break
        if check_name_func(nombre,cliente_id_actual): #check_name_func ya recibe usuario_sistema_id
            print("---ADVERTENCIA---")
            print(f"ERROR: el nombre '{nombre}' ya existe para tu usuario\nNo se actulizara el nombre\n") #no agregamos a updates{} si ya existe
        else:
            updates['nombre'] = nombre # -/- insertamos nombre en el diccionario -/-
            
    #Telefono
    #------------------------------------------------------------------
    telefono = clean_input(
        f"| Nuevo telefono (actual: {cliente_existente[2] if cliente_existente[2] else 'N/A'}): (Deje vacio omitir, escriba 'NULL' para borrar)\n",
        min_len=0,
        max_len=10,
        allow_empty=True,
        to_none_on_empty=False, #retorna una cadena vacia "", no queremos retornar None
        special_null_keyword='NULL'
    )
    #Caso 1. El usuario quiere borrar el numero ingreso NULL
    if telefono is None: #validamos que el telefono, no esta vacio, no es None,
        updates['telefono'] = None # -/- insertamos None en el diccionario -/-
        print(" Numero de Telefono Borrado\n")
    #Caso 2. El Usuario no ingreso nada (omitio el campo) o solo ingreso espacios
    elif telefono == "":
        print(" Telefono no modificado\n")
        pass
    #Caso 3. El usuario ingreso un valor diferente a NULL y no vacio
    else:
        #primero verificamos que el  numero no sea igual
        if telefono.strip() == cliente_existente[2]:
            print(f" El numero {telefono} es el mismo que el actual\nNo se actualizo el telefono\n")
        #si no es igual validamos que sea un numero
        elif telefono.isdigit():
            updates['telefono'] = telefono #si todo va bien añadimos al diccionario
            print(f" Numero de Telefono Actualizado a {telefono}\n")
        else:
            #esto es solo si no es NULL, vacio, no es igual, y no es solo digitos
            print(f" WARN: problema con el valor ingresado {telefono}\nNo se actualizo el telefono\n")


    #Ubicacion
    #----------------------------------------------------------------------------
    ubicacion = clean_input(
        # pyrefly: ignore  # bad-specialization
        f"| Nueva ubicacion aproximada (actual: {cliente_existente[3] if cliente_existente[3] else 'N/A'})\n",
        allow_empty=True,
        to_none_on_empty=False,
        special_null_keyword='NULL'
    )
    if ubicacion is not None and ubicacion != "":
        updates["ubicacion_aproximada"] = ubicacion
    elif ubicacion is None: #si el usuario escribio NULL
        updates["ubicacion_aproximada"] = None
        
    # Foto Domicilio
    #----------------------------------------------------------------------------
    foto_domicilio = clean_input(
        # pyrefly: ignore  # bad-specialization
        f"| URL de la foto (actual: {cliente_existente[4] if cliente_existente[4] else 'N/A'})\n",
        allow_empty=True,
        to_none_on_empty=False,
        special_null_keyword='NULL'
    )
    if foto_domicilio is not None and foto_domicilio != "":
        updates["foto_domicilio"] = foto_domicilio
    elif foto_domicilio is None: #si el usuario escribio NULL
        updates["foto_domicilio"] = None

    #Comentario
    #--------------------------------------------------------------------------------
    comentario = clean_input(
        # pyrefly: ignore  # bad-specialization
        f"| Nuevo comentario (actual: {cliente_existente[5] if cliente_existente[5] else 'N/A'})\n",
        allow_empty=True,
        to_none_on_empty=False,
        special_null_keyword='NULL'
    )
    if comentario is not None and comentario != "":
        updates["comentario"] = comentario
    elif comentario is None: #si el usuario escribio NULL
        updates["comentario"] = None
    
    #------------------------------------------------------------------------------------
    
    return updates

#--- SOLICITAMOS EL MONTO DEL CLIENTE ---
def solicitar_monto_actualizacion():
    """Solicitamos el monto y lo validamos
    returs Decimal or None"""
    while True:
        monto_str = input(
            "\n Ingrese el monto a aplicar\n"
            "| -AÑADIR- Saldo (ej: 00.00)\n"
            "| -RESTAR- Saldo (ej: -00.00)\n"
            "| deje en blanco para cancelar\n"
            "| =>  "
            )
        if not monto_str:
            return None #usuario cancelo la operacion
        #convertimos a decimal
        try:
            monto = Decimal(monto_str) #convertimos a decimal
            if monto == 0:
                print(" El monto no puede ser '0', intente de nuevo")
                continue
            return monto #retornamos el monto
        except InvalidOperation: #atrapamos el error
            print(" Monto Invalido, intente de nuevo.\nEj: 00.00 para añadir al saldo\n  -00.00 para restar al saldo")
        except Exception as e:
            print(f"---ERROR INESPERADO---\n{e}")

#--- SOLICITA EL NUEVO ESTADO DEL CLIENTE ---
def solicitar_nuevo_estado():
    """Muestra las opciones, solicita y lo valida"""
    estados_validos = {
        '1': 'regular',
        '2': 'moroso',
        '3': 'bueno',
        '4': 'inactivo'
    }
    print("Seleccione un nuevo estado para el cliente: ")
    for numero, estado in estados_validos.items():
        print(f"{numero}. {estado.upper()}")
    while True:
        opcion = input("| Ingrese una opcion: 1 - 4\n").strip()
        if opcion in estados_validos:
            return estados_validos[opcion]
        else:
            print("\n---OPCION INVALIDA---\nIngrese un numero del 1 al 4\n")




