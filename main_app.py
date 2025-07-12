#////////------- IMPORTS ---------//////
from db.operations import (
    crear_tabla_clientes,
    agregar_cliente,
    obtain_clients,
    client_update,
    eliminar_cliente,
    client_search,
    list_client,
    actualizar_saldo
)
from datetime import date #importamos fecha
from decimal import Decimal, InvalidOperation #importamos decimal para uso futuro con saldos


#####-------//////INICIO DE LA LOGICA DE PRUEBA/////--------######
#Establecemos los id del usuario actual fijo temporalmente    
USER_ID = 1

#////---- FUNCION PARA EL MENU ----////
def menu():
    """Muestra las opciones del menú"""
    print("\nMENU DEL GESTOR DE CLIENTES\n")
    print("1. Agregar nuevo cliente")
    print("2. Buscar cliente")
    print("3. Modificar cliente existente")
    print("4. Obtener todos los clientes")
    print("5. Eliminar cliente")
    print("6. Actualizar Saldo")
    print("7. Salir")
    print("-------------------------------\n")

#funcion para obtener un id de cliente valido
def obtener_client_id():
    while True:
        try:
            client_id = int(input("\nIngrese el ID del cliente seleccionado: \n")) #pedimos el ID validando que sea un numero
            if client_id <= 0: #validamos que mayor a cero
                print("\nEl ID no puede ser negativo o cero. Intente de nuevo.\n")
            else:
                break #salimos del bucle si el ID es valido
        except ValueError: #atrapamos el error si no es un numero y reinciamos el bucle
            print("Entrada invalida. Por favor, ingrese un numero entero para el ID.\n")
    return client_id

#////---- FUNCION PARA SOLICITAR DATOS ----////
def info_data(): #de esta variable obtenemos los datos para añadir clientes o modificarlos
    """Solicita la informacion del cliente al usuario, usamos validacion basica.
    Retorna un diccionario con los datos o None si la validacion falla"""

    print("----INGRESE DATOS DEL CLIENTE NUEVO----")
    #nos aseguramos que el nombre no este vacio
    while True:
        nombre = input("Nombre (OBLIGATORIO): formato 'Nombre Apellido'\n ").strip()
        if nombre: #declarar el if de esta forma indica 'si el nombre no esta vacio'
            break
        else:
            print("El nombre no puede estar vacio, Intente de nuevo...\n ")
    
    while True:
        nombre_sin_espacios = nombre.replace(" ", "") #type: ignore
        if len(nombre_sin_espacios) < 3:
            print("El nombre debe tener al menos 3 caracteres \n")
        else:
            break
        
    while True:
        telefono = input("Telefono: (Deje vacio para omitir): ").strip()
        telefono_sin_espacios = telefono.replace(" ", "")
        if not telefono_sin_espacios: #esta es la forma de validar si una cadena esta vacia
            break #si esta vacio, rompemos el bucle
        elif len(telefono_sin_espacios) != 10:
            print("-ERROR- el telefono debe tener 10 digitos.")
        else: #si el input tiene 10 digitos y no esta vacio rompemos el bucle
            break

    #solicitamos las entradas pero no agregamos mucha validacion
    ubicacion = input("Ubicacion Aproximada: \n").strip()
    foto_domicilio = input("ingrese la ruta a la foto del domicilio").strip()
    comentario = input("Comentario").strip()

    return {
        "nombre": nombre,
        "telefono": telefono_sin_espacios if telefono_sin_espacios else None, #almacenamos en la DB el numero limpio y sin espacios
        "ubicacion": ubicacion if ubicacion else None,
        "foto_domicilio": foto_domicilio if foto_domicilio else None,
        "comentario": comentario if comentario else None
    }

#////---- MANEJO PARA AGREGAR CLIENTES ----////
def new_client():
    """Funcion dependiente de la solicitud de datos, para agregar los clientes"""
    datos = info_data()
    if datos: #si se obtuvieron datos validos, nombre valido/obligatorio
        agregar_cliente(
            datos["nombre"],
            datos["telefono"],
            datos["ubicacion"],
            datos["foto_domicilio"],
            datos["comentario"],
            USER_ID
        )

#////---- Funcion para buscar un cliente, obtener el id y los datos ----////
def busqueda():
    search_name = input("Ingresa el cliente para buscar, solo ingresa el primer nombre : \n")
    client_search(search_name, USER_ID)

#////---- Funcion para obtener todos los clientes de un usuario ----////
def ver_clientes():
    obtain_clients(USER_ID)

#////---- Funcion para actualizar los clientes de un usuario ----////
def manejo_actualizacion():
    """Manejo de la logica para modificar clientes"""
    print("\n---ACTUALIZANDO DATOS DE CLIENTE---\n")
    busqueda() #mostramos los clientes para que el usuario sepa que ID elegir
    client_id = obtener_client_id()
    # while True:
    #     try:
    #         client_id = int(input("\nIngrese el ID del cliente a actualizar: \n")) #pedimos el ID validando que sea un numero
    #         if client_id <= 0: #validamos que mayor a cero
    #             print("\nEl ID no puede ser negativo o cero. Intente de nuevo.\n")
    #         else:
    #             break #salimos del bucle si el ID es valido
    #     except ValueError: #atrapamos el error si no es un numero y reinciamos el bucle
    #         print("Entrada invalida. Por favor, ingrese un numero entero para el ID.\n")
    
    print("\nINGRESE LOS NUEVOS VALORES PARA LOS CAMPOS A ACTUALIZAR (DEJE EN BLANCO PARA NO ACTUALIZAR, ESCRIBA 'NULL' PARA BORRAR VALOR ACTUAL)\n")
    updates = {} #creamos un diccionario vacio para almacenar los valores
    
    #validamos que el campo nombre no este vacio
    while True:
        nombre_input = input(f"Nuevo nombre, deje vacio omitir, escriba 'NULL' para borrar\n").strip()
        if not nombre_input: #si nombre_input esta vacio omitimos
            print("Omitiendo el cambio de nombre\n")
            break
        elif nombre_input.upper() == 'NULL': #no permitimos el nombre NULL
            print("El nombre no puede ser 'NULL', ingrese un nombre o deje vacio\n")
        elif not nombre_input: #si despues del strip, el nombre sigue vacio, si eran solo espacios
            print("El nombre no pueden ser espacios, ingrese un nombre o deje en blanco\n")
        else:
            updates['nombre'] = nombre_input
            print(f"Nombre actualizado a {nombre_input}\n")
            break #rompemos el bucle si el nombre cumple con nuestras condiciones
    while True:
        telefono = input("Nuevo telefono: (Deje vacio omitir, escriba 'NULL' para borrar): \n").strip()
        print("")
        telefono_sin_espacios = telefono.replace(" ", "")
        if not telefono_sin_espacios: #esta es la forma de validar si una cadena esta vacia
            # updates['telefono'] = telefono if telefono.upper() != 'NULL' else None
            break #rompemos el bucle si no hay 
        elif len(telefono_sin_espacios) != 10:
            print("-ERROR- el telefono debe tener 10 digitos.\n")
        else:
            updates['telefono'] = telefono_sin_espacios if telefono_sin_espacios.upper() != 'NULL' else None
            break
            
    ubicacion = input("Nueva ubicacion aproximada (Deje vacio omitir, escriba 'NULL' para borrar)\n").strip()
    if ubicacion: #si ubicacion no esta vacio
        updates['ubicacion_aproximada'] = ubicacion if ubicacion.upper() != 'NULL' else None
    
    foto_domicilio = input("Nueva ruta a la foto del domicilio (Deje vacio omitir, escriba 'NULL' para borrar)\n").strip()
    if foto_domicilio: #si foto domicilio no esta vacio
        updates['foto_domicilio'] = foto_domicilio if foto_domicilio.upper() != 'NULL' else None
    
    comentario = input("Nuevo comentario (Deje vacio omitir, escriba 'NULL' para borrar)\n").strip()
    if comentario: #si comentario no esta vacio
        updates['comentario'] = comentario if comentario.upper() != 'NULL' else None
    
    #si no hay cambios ingresados
    if not updates: #si no hay datos almacenados en updates{}
        print("No se ingresaron datos para actualizar\nNo se actualizó el cliente\n")
        list_client(client_id, USER_ID)
        return
    
    client_update(client_id, USER_ID, **updates)

#////---- Funcion para actualizar saldo del cliente ----////
def manejo_saldo():
    """Manejo de la logica para modifica saldo del cliente"""
    print("\n---ACTUALIZANDO SALDO DE CLIENTE---\n")
    busqueda()
    client_id = obtener_client_id()
    print(f"Mostrando saldo actual")
    list_client(client_id, USER_ID)

    #solicitamos el monto a restar o sumar y toca validarlo
    while True:
        monto_str = input("Ingrese el monto\npara añadir saldo solo escriba el monto seguido de 2 decimales\nEj: 00.00\npara restar al saldo escriba el signo '-' seguido del monto\nEj: -00.00\n\n")
        try:
            monto = Decimal(monto_str) #convertimos a decimal
            break
        except InvalidOperation: #atrapamos el error
            print("Monto Invalido, intente de nuevo.\nEj: 00.00 para añadir al saldo\n  -00.00 para restar al saldo")
        except Exception as e:
            print(f"Ocurrio un error inesperado al actualizar el monto:\n{e}, intente de nuevo\n Ej: 00.00 para añadir al saldo\n  -00.00 para restar al saldo")
    #una vez validado el monto, llamamos a la funcion con la sentencia
    if actualizar_saldo(client_id, USER_ID, monto):
        print(f"Saldo Actual:\n")
        list_client(client_id, USER_ID)
    else:
        print("No se pudo actualizar el saldo")

#////---- Funcion para eliminar los clientes de un usuario ----////
def manejo_delete():
    """Manejo de la logica para eliminar clientes"""
    print("\n---ELIMINANDO CLIENTE---\n")
    busqueda() #mostramos los clientes para que el usuario sepa que ID elegir
    client_id =obtener_client_id()
    # while True:
    #     try:
    #         client_id = int(input("\nIngrese el ID del cliente a eliminar: \n")) #pedimos el ID validando que sea un numero
    #         if client_id <= 0: #validamos que mayor a cero
    #             print("\nEl ID no puede ser negativo o cero. Intente de nuevo.\n")
    #         else:
    #             break #salimos del bucle si el ID es valido
    #     except ValueError: #atrapamos el error si no es un numero y reinciamos el bucle
    #         print("Entrada invalida. Por favor, ingrese un numero entero para el ID.\n")

    #confirmamos si el cliente es correcto
    list_client(client_id, USER_ID)
    while True:
        confirmacion = input(f"Seguro que desea eliminar el cliente con ID: {client_id}\n//--   S/N   --//\n")
        if confirmacion.upper() != 'S':
            print("Omitiendo eliminacion -- Operacion cancelada\n---   NO SE ELIMINARON DATOS  ---")
            break
        elif confirmacion:
            print("SE ELIMINO EL CLIENTE")
            list_client(client_id, USER_ID)
            eliminar_cliente(client_id, USER_ID)
            break

#////---- Funcion principal de la CLI ----////
def main_cli():
    #creamos la tabla siempre al inciar
    if not crear_tabla_clientes():
        print("\n-/- ERROR -/-\n-/-NO SE PUDO INICIALIZAR LA BASE DE DATOS-/-/\n-/-/-SALIENDO-/-/\n")
        return
    
    while True:
        menu()
        opcion = input("\nIngrese una opcion: 1 - 6\n").strip()
        
        if opcion == '1':
            new_client()
        elif opcion == '2':
            busqueda()
        elif opcion == '3':
            manejo_actualizacion()
        elif opcion == '4':
            ver_clientes()
        elif opcion == '5':
            manejo_delete()
        elif opcion == '6':
            manejo_saldo()
        elif opcion == '7':
            print("\nSALIENDO DEL PROGRAMA...\n")
            break
        else:
            print("--OPCION NO VALIDA--\n--NGRESE UN NUMERO DEL 1 AL 6--\n")




if __name__ == "__main__":

    main_cli()