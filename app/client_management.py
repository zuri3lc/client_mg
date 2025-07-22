# Este modulo contiene la logica para la gestion de los clientes
from .utils import (
    obtener_client_id,
    )
from .database import (
    obtain_clients_db,
    get_username_by_id_db,
    client_search_db,
    historial_movimientos_db,
    list_client_db
    )
from .user_interface import (
    mostrar_clientes,
    mostrar_historial_movimientos)

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
    
    search_name = input(" Ingresa el cliente para buscar, ingresa el primer nombre : \n").strip()
    
    if not search_name:
        print("\n ERROR: La busqueda no puede estar vacia")
        return

    clientes_encontrados = client_search_db(search_name, usuario_sistema_id)
    if not clientes_encontrados:
        print(f"\nNo se encontraron resultados para '{search_name}'.\n")
        return
    print(f"Resultados para la busqueda '{search_name}: ")
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
        nombre_cliente = cliente_existente[1]
        print(f"\n--- No se encontraron movimientos para: {nombre_cliente}, ID {client_id} ---\n")
        return
    # 5 llamamos al especialista de la interfaz para mostrar el historial
    mostrar_historial_movimientos(movimientos)

def mostrar_cliente_detalle(cliente):
    """Toma la unica fila y la formatea"""
    if not cliente:
        print(f"---ERROR---\nNo se pudieron obtener los datos del cliente...\n")
        return
    id_cliente = cliente[0]
    nombre = cliente[1]
    telefono = cliente[2]
    ubicacion = cliente[3]
    foto_domicilio = cliente[4]
    comentario = cliente[5]
    fecha_creacion = cliente[6].strftime("%d/%m/%Y")
    ultima_modificacion = cliente[7].strftime("%d/%m/%Y")
    saldo = cliente[8]
    estado = cliente[9]
    



