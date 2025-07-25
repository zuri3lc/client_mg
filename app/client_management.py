# Este modulo contiene la logica para la gestion de los clientes
from .utils import (
    obtener_client_id,
    )
from .database import (
    obtain_clients_db,
    get_username_by_id_db,
    client_search_db,
    historial_movimientos_db,
    list_client_db,
    check_client_name_exist_db,
    agregar_cliente_db,
    client_update_db,
    actualizar_saldo_db,
    eliminar_cliente_db
    )
from .user_interface import (
    mostrar_clientes,
    solicitar_datos_actualizacion,
    mostrar_historial_movimientos,
    solicitar_nombre_cliente,
    mostrar_cliente_detalle,
    solicitar_info_clientes,
    solicitar_monto_actualizacion,
    solicitar_nuevo_estado
    )

#---- Funcion para obtener todos los clientes de un usuario ----
def ver_clientes(usuario_sistema_id):
    clientes = obtain_clients_db(usuario_sistema_id)
    print("\n---- MIS CLIENTES ----\n")
    #llamamos a la funcion asignandole una variable al resultado
    clientes = obtain_clients_db(usuario_sistema_id)
    if not clientes: #si la consulta no obtiene nada
        nombre_usuario = get_username_by_id_db(usuario_sistema_id)
        print(f"No se encontraron clientes para el usuario {nombre_usuario}\n")
        return #sale de la funcion retornando una lista vacia
    #llamamos a la funcion que va a mostrar los datos
    mostrar_clientes(clientes)

#---- Funcion para buscar un cliente, obtener el id y los datos ----
def busqueda(usuario_sistema_id):
    print("\n--- BUSQUEDA DE CLIENTES ---\n")
    
    search_name = input("Ingresa el cliente para buscar, ingresa el primer nombre : \n").strip()
    
    if not search_name:
        print("\nERROR: La busqueda no puede estar vacia")
        return

    clientes_encontrados = client_search_db(search_name, usuario_sistema_id)
    if not clientes_encontrados:
        print(f"\nNo se encontraron resultados para '{search_name}'.\n")
        return
    print(f"\nResultados para la busqueda '{search_name}: ")
    mostrar_clientes(clientes_encontrados)

# ------- MANEJA EL HISTORIAL DE MOVIMIENTOS --------
def manejo_historial(usuario_sistema_id):
    """Logica para mostrar el historial de movimientos de un cliente"""
    print("\n---CONSULTAR HISTORIAL DE MOVIMIENTOS---\n")
    busqueda(usuario_sistema_id)
    # 1 obtenemos un id valido
    client_id = obtener_client_id()
    # 2 validamos que el cliente exista
    cliente_existente = list_client_db(client_id, usuario_sistema_id)
    if not cliente_existente:
        print(f"\n---ERROR---\nCliente no encontrado con ID: {client_id} o no te pertence")
        return
    # 3 llamamos al especialista de DB para obtener los movimientos
    movimientos = historial_movimientos_db(client_id, usuario_sistema_id)
    # 4 manejamos el caso de que no haya movimientos
    if not movimientos:
        nombre_cliente = cliente_existente['nombre']
        print(f"\n--- No se encontraron movimientos para: {nombre_cliente}, ID {client_id} ---\n")
        return
    # 5 llamamos al especialista de la interfaz para mostrar el historial
    mostrar_historial_movimientos(movimientos)

# --- CREA UN NUEVO CLIENTE ---
def crear_nuevo_cliente(usuario_sistema_id):
    """Orquesta el proceso de creacion de un cliente
    1. pide el nombre del cliente UI
    2. verifica si ya existe DB
    3. pide el resto de la informacion UI
    4. guarda el cliente en la base de datos DB
    5. muestra el resultado UI"""
    print("\n---CREANDO NUEVO CLIENTE---\n")
    #paso 1. obtenermos el nombre en la  UI
    #se pasa la funcion de verificacion como argumento (DES-ACOPLAMOS)
    nombre_cliente = solicitar_nombre_cliente(
        lambda nombre: not check_client_name_exist_db(nombre, usuario_sistema_id) #esta es la funcion de validacion
    )
    #si el usuario cancela o hubo un error en la validacion
    if not nombre_cliente:
        print("\nOperacion cancelada.")
        return
    #paso 2. usar la interfaz para solicitar los demas datos
    datos_adicionales = solicitar_info_clientes()
    #combinamos la informacion en el diccionario
    datos_cliente = {
        "nombre": nombre_cliente,
        **datos_adicionales, #desempaquetamos el diccionario
        "usuario_sistema_id": usuario_sistema_id #añadimos el usuario del sistema a los datos
    }
    
    #paso 3. llamamos al especialista y le pasamos los datos
    cliente_id = agregar_cliente_db(**datos_cliente)
    
    #paso 4. usamos la interfaz para mostrar los resultados
    if cliente_id:
        print("\n---- CLIENTE AGREGADO EXITOSAMENTE ----\n")
        nuevo_cliente = list_client_db(cliente_id, usuario_sistema_id)
        mostrar_cliente_detalle(nuevo_cliente)
    else:
        print("\n--- ERROR: No se pudo agregar el cliente ---\n")

#--- ACTUALIZACION DEL CLIENTE ---
def actualizar_cliente(usuario_sistema_id):
    print("---ACTUALIZANDO DATOS---")
    #1. llamamos a busqueda para buscar al usuario que necesitamos
    busqueda(usuario_sistema_id)
    #2. Obtenemos un ID de cliente valido
    client_id = obtener_client_id()
    cliente_existente = list_client_db(client_id, usuario_sistema_id)
    
    if not cliente_existente:
        print(f"\n---ERROR---\nCliente con ID: {client_id} no encontrado o no te pertenece")
        return
    #3. llamamos a la interfaz de usuario para que pida los nuevos datos
    #aqui pasamois el cliente existente y la funcion de validacion
    updates = solicitar_datos_actualizacion(
        cliente_existente,
        lambda nombre, exclude_id: check_client_name_exist_db(nombre, usuario_sistema_id, exclude_id)
    )

    #4 la validacion del nombre ya la estamos manejando en user_interface
    #5 si hay datos para actualizar llamamos a la DB
    if not updates:
        print("No se ingresaron datos nuevos para actualizar\n---CANCELANDO---\n")
        return
    if client_update_db(client_id, usuario_sistema_id, **updates):
        print("\n--- DATOS ACTUALIZADOS EXITOSAMENTE ---\n")
        cliente_actualizado = list_client_db(client_id, usuario_sistema_id)
        mostrar_cliente_detalle(cliente_actualizado)
    else:
        print("\n--- ERROR: No se pudo actualizar el cliente ---\n")

#--- ACTUALIZACION DEL SALDO ---
def gestionar_actualizacion_saldo(usuario_sistema_id):
    print("\n--- ACTUALIZANDO SALDO ---\n")
    #1. el usuario encuentra el cliente
    busqueda(usuario_sistema_id)
    #2 obtenemos ID valido del cliente
    client_id = obtener_client_id()
    cliente_existente = list_client_db(client_id, usuario_sistema_id)
    if not cliente_existente:
        print(f"\n---ERROR---\nCliente no encontrado con ID: {client_id} o no te pertence")
        return
    print("\nCliente a modificar: \n")
    mostrar_cliente_detalle(cliente_existente)
    #2.1 mostramos los ultimos 3 movimientos del cliente
    movimientos = historial_movimientos_db(client_id, usuario_sistema_id, limite=3)
    mostrar_historial_movimientos(movimientos)
    #3 llamamos a la UI para solicitar el monto
    monto = solicitar_monto_actualizacion()
    if monto is None:
        print("\nOperacion cancelada. No  se ingreso un monto valido\n")
        return
    #4 llamamos a la DB para actualizar el saldo
    if actualizar_saldo_db(client_id, usuario_sistema_id, monto):
        print("\n--- SALDO ACTUALIZADO EXITOSAMENTE ---\n")
        cliente_actualizado = list_client_db(client_id, usuario_sistema_id)
        mostrar_cliente_detalle(cliente_actualizado)
    else:
        print("\n--- ERROR: No se pudo actualizar el saldo ---\n")

#////---- ELIMINAR UN CLIENTE ----////
def gestionar_eliminacion_cliente(usuario_sistema_id):
    """Manejo de la logica para eliminar clientes"""
    print("\n---ELIMINANDO CLIENTE---\n")
    print("\n---VERIFIQUE DOS VECES EL CLIENTE A ELIMINAR---\n")
    #1. ayudamos al usuario a buscar el cliente
    busqueda(usuario_sistema_id)
    client_id = obtener_client_id()
    #2. verificamos que el cliente exista
    cliente_existente = list_client_db(client_id, usuario_sistema_id)
    if not cliente_existente:
        print(f"\n---ERROR---\nCliente no encontrado con ID: {client_id} o no te pertence")
        return
    #3. confirmamos si el cliente es correcto
    nombre = cliente_existente['nombre']
    #4. llamamos a la UI que muestre los datos del cliente
    mostrar_cliente_detalle(cliente_existente)
    #5. solicitamos confirmacion
    while True:
        confirmacion = input(f"Seguro que desea eliminar el cliente con ID: {client_id} (Nombre: {nombre})\n//--   S/N   --//\n").strip().upper()
        if confirmacion == 'N':
            print(" Omitiendo eliminacion -- Operacion cancelada\n ===  NO SE ELIMINARON DATOS  ===")
            break
        elif confirmacion == 'S':
            #si el usuario confirma llamamos al especialista de la DB
            if eliminar_cliente_db(client_id, usuario_sistema_id): #llamamos a la funcion para eliminar, si retona True se ejecuta lo siguiente
                print(f" SE ELIMINO EL CLIENTE CON ID: {client_id} ({nombre})")
                break
            else:
                print(" ERROR: No se pudo eliminar el cliente")
                break
        else: # si ingresan algo diferente a S o N
            print(" Entrada Invalida, ingrese S para eliminar o N para cancelar\n")

# ---GESTIONA EL ESTADO DEL CLIENTE ----
def gestionar_actualizacion_estado(usuario_sistema_id):
    print("\n--- ACTUALIZANDO ESTADO ---\n")
    # 1. pedimos al usuario que busque el cliente
    busqueda(usuario_sistema_id)
    # 2. obtenemos un id valido
    client_id = obtener_client_id()
    #3. Validamos que el cliente exista
    cliente_existente = list_client_db(client_id, usuario_sistema_id)
    if not cliente_existente: #si no lo encuentra
        print(f"\n---ERRROR---\nCliente con ID: {client_id} no encontrado")
        return
    #4 .mostramos el cliente que se va a modificar
    print("VAS A MODIFICAR EL SIGUIENTE CLIENTE: \n")
    mostrar_cliente_detalle(cliente_existente)
    #5. solicitamos el nuevo estado
    nuevo_estado = solicitar_nuevo_estado()
    #6. llamamos al especialista en la db, reutilizamos client_update_db
    print(f"\nActualizando estado a {nuevo_estado}...\n")
    if client_update_db(client_id, usuario_sistema_id, estado_cliente=nuevo_estado):
        print("\n--- ESTADO ACTUALIZADO EXITOSAMENTE ---\n")
        cliente_actualizado = list_client_db(client_id, usuario_sistema_id)
        mostrar_cliente_detalle(cliente_actualizado)
    else:
        print("\n--- ERROR: No se pudo actualizar el estado ---\n")

