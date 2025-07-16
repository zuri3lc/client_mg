#////////------- IMPORTS ---------//////
from db.operations import (
    crear_tabla_clientes,
    agregar_cliente,
    obtain_clients,
    client_update,
    eliminar_cliente,
    client_search,
    list_client,
    actualizar_saldo,
    sys_usr,
    check_client_name_exist
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
    print(f"BIENVENIDO  {sys_usr(USER_ID)}, Que deseas hacer?\n")
    print("1. Agregar nuevo cliente")
    print("2. Buscar cliente")
    print("3. Modificar cliente existente")
    print("4. Obtener todos los clientes")
    print("5. Eliminar cliente")
    print("6. Actualizar Saldo")
    print("7. Salir")
    print("-------------------------------\n")

#////---- Funcion principal de la CLI ----////
def main_cli():
    #creamos la tabla siempre al inciar
    if not crear_tabla_clientes():
        print("\n-/- ERROR -/-\n-/-NO SE PUDO INICIALIZAR LA BASE DE DATOS-/-/\n-/-/-SALIENDO-/-/\n")
        return
    
    while True:
        menu()
        opcion = input("\nIngrese una opcion: 1 - 7\n").strip()
        
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

#////---- FUNCION PARA LIMPIAR Y PROCESAR ENTRADAS DE USUARIO ----////
def clean_input(promt, min_len=0, max_len=255, allow_empty=True, to_none_on_empty=False, special_null_keyword=None):
    """SOLICITA UNA ENTRADA AL USUARIO, LA LIMPIA Y LA VALIDA
    Args:
        promt (str): el mensaje que se muestra a usuario
        min_len (int): longitud minima (sin espacios)
        max_len (int): longitud maxima (sin espacios)
        allow_empty (bool): Si es True la entrada esta vacia o es None, retorna None
                    util para campos opcionales
        special_null_keyword (str, opcional): una palabra clave que el usuario puede escribir
                                para que se interprete como None
                                            
        returns:
            str or None: La entrada limpia y valida o None si esta vacia o nula
        """
    while True:
        user_input = input(promt).strip() #elimina los espacios vacios al principio y al final
        
        #convertimos a None si se usa la palabra clave
        if special_null_keyword and user_input.upper() == special_null_keyword.upper():
            return None
        
        #entrada vacia
        if not user_input:
            if allow_empty:
                #si se permite vacio convertimos a None
                return None if to_none_on_empty else ""
            else:
                print(f"Este campo no puede estar vacio, intente de Nuevo\n")
                continue
        
        #validamos longitud minima
        if len(user_input.replace(" ", "")) < min_len: #contamos los caracteres sin espacios
            print(f"El campo debe tener al menos {min_len} caracteres\n")
            continue
        
        #validamos longitud maxima
        if len(user_input.replace(" ", "")) > max_len:
            print(f"El campo debe tener menos de {max_len} caracteres\n")
            continue
        
        return user_input #retorna la entrada limpia y validada

#-------- VALIDAR QUE EL CLIENTE EXISTA  O LE PERTENEZCA AL USUARIO ------
def validar_cliente():
    while True:
        client_id = obtener_client_id()
        cliente_existente = list_client(client_id, USER_ID)
        if cliente_existente:
            break #si el cliente existe salimos del bucle
        else:
            print("\n--ERROR--\n--El cliente no existe o no pertenece a tu usuario--\n--Intenta de Nuevo--\n")
    return client_id, cliente_existente #fuera del bucle retornamos el id para usarlo en otras funciones

#////---- FUNCION PARA SOLICITAR DATOS ----////
def info_data(initial_name=None): #de esta variable obtenemos los datos para añadir clientes o modificarlos
    """Solicita la informacion del cliente al usuario.
    Retorna un diccionario con los datos o None si la validacion falla"""

    print("----INGRESE DATOS DEL CLIENTE NUEVO----")
    data = {} #creamos un diccionario vacio para almacenar los datos
    
    if initial_name: #si ya tenemos un nombre valido lo usamos
        data["nombre"] = initial_name
    else: #si no, pedimos el nombre, aqui no hay prevalidacion
        #usamos clean_input para validar, no permitimos vacios y validamos longitud
        data["nombre"] = clean_input(
            "Nombre (OBLIGATORIO): formato 'Nombre Apellido' min 3 caracteres, max 255: \n",
            min_len=3, #le decimos que queremos un minimo de caracteres
            max_len=255, # y un maximo de 255
            allow_empty=False #no permitimos que esta entrada se quede vacia
        )
        #-----en vez de validar con todo lo que esta debajo de esta linea, lo hacemos, solo con una linea de codigo-----
        # while True:
        #     nombre = input("Nombre (OBLIGATORIO): formato 'Nombre Apellido' min 3 caracteres, max 255: \n ").strip()
        #     nombre_sin_espacios = nombre.replace(" ", "") #type: ignore
        #     if not nombre_sin_espacios: # 'si el nombre esta vacio'
        #         print("El nombre no puede estar vacio, Intente de nuevo...\n ")
        #     elif len(nombre_sin_espacios) < 4:
        #         print("El nombre debe tener al menos 3 caracteres \n")
        #     elif len(nombre_sin_espacios) > 255:
        #         print("El nombre debe tener menos de 255 caracteres \n")
        #     else:#declarar el if de esta forma indica 'si el nombre no esta vacio'
        #         data["nombre"] = nombre # -/- insertamos nombre en el diccionario -/-
        #         break
    
    #---- Lo mismo sucede con el telefono, nos ahorramos todas las lineas de codigo y solo usamos una bien estructurada con clean_input -------
    
    while True:
        telefono = clean_input(
            "Telefono: (Deje vacio para omitir): \n",
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
            print("-ERROR- el telefono debe tener 10 digitos.")

    # while True:
    #     telefono = input("Telefono: (Deje vacio para omitir): \n").strip()
    #     telefono_sin_espacios = telefono.replace(" ", "")
    #     if not telefono_sin_espacios: #esta es la forma de validar si una cadena esta vacia
    #         break #si esta vacio, rompemos el bucle
    #     elif telefono_sin_espacios.isdigit() and len(telefono_sin_espacios) == 10:
    #         data['telefono'] = telefono_sin_espacios # -/- insertamos telefono limpio en el diccionario -/-
    #         break # si el imput tiene 10 digitos y no esta vacio rompemos el bucle
    #     else: #si el input no tiene 10 digitos volvemos a empezar
    #         print("-ERROR- el telefono debe tener 10 digitos.")

    #solicitamos las demas entradas
    #permitimos vacio y convertimos a None para la DB
    
    data["ubicacion"] = clean_input(
            "Ubicaion aproximada: (Deje vacio para omitir)\n",
            allow_empty=True,
            to_none_on_empty=True
        )
    
    data["foto_domicilio"] = clean_input(
            "Ingrese la ruta a la foto del Domicilio: (Deje vacio para omitir)\n",
            allow_empty=True,
            to_none_on_empty=True
    )

    data["comentario"] = clean_input(
            "Comentario: (Deje vacio para omitir)\n",
            allow_empty=True,
            to_none_on_empty=True
    )


    return data

#////---- MANEJO PARA AGREGAR CLIENTES ----////
def new_client():
    """Funcion dependiente de la solicitud de datos, para agregar los clientes"""
    
    validated_name = None

    while True:
            nombre_input = input("Nombre (OBLIGATORIO): formato 'Nombre Apellido' min 3 caracteres, max 255: \n ").strip()
            nombre_sin_espacios = nombre_input.replace(" ", "") #type: ignore
            if not nombre_sin_espacios: # 'si el nombre esta vacio'
                print("El nombre no puede estar vacio, Intente de nuevo...\n ")
                continue
            elif len(nombre_sin_espacios) < 4:
                print("El nombre debe tener al menos 3 caracteres \n")
                continue
            elif len(nombre_sin_espacios) > 254:
                print("El nombre debe tener menos de 255 caracteres \n")
                continue
            
            if check_client_name_exist(nombre_input, USER_ID):
                print(f"ERROR: el nombre '{nombre_input}' ya existe para tu usuario {sys_usr(USER_ID)}\n")
                continue
            else:
                validated_name = nombre_input #guardamos el nombre validado
                break #salimos del bucle
    
    
    datos = info_data(initial_name=validated_name)
    client_id = agregar_cliente(
            datos["nombre"],
            datos["telefono"],
            datos["ubicacion"],
            datos["foto_domicilio"],
            datos["comentario"],
            USER_ID
        )
    if client_id:
        list_client(client_id, USER_ID)
    else:
        print("No se pudo agregar el cliente debido a un error en la base de datos")

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
    client_id, cliente_existente = validar_cliente() #obtenemos los 2 valores que retorna validar_cliente()

    print("\nINGRESE LOS NUEVOS VALORES PARA LOS CAMPOS A ACTUALIZAR (DEJE EN BLANCO PARA OMITIR CAMPO, ESCRIBA 'NULL' PARA BORRAR VALOR ACTUAL)\n")
    updates = {} #creamos un diccionario vacio para almacenar los valores
    
    #------------------------------------------------------------------
    #usamos clean_input para validar
    #min_len=0 y max_len=255 son valores por defecto, asi que solo los escribirmos si necesitamos cambiarlos
    #allow_empty=True nos permite dejar un campo vacio
    #to_none_on_empty=False Si esta vacio NO lo convertimos a None porque en este caso el usuario no desea cambiar el valor
    #special_null_keyword='NULL' si el usuario escribe NULL convertimos a None para eliminar el valor
    #------------------------------------------------------------------
    
    #Nombre
    #------------------------------------------------------------------
    nombre = clean_input(
        # pyrefly: ignore  # bad-specialization
        f"Nuevo nombre (actual: {cliente_existente[1]}): formato 'Nombre Apellido' min 3 caracteres, max 255\n",
        min_len=3,
        max_len=255,
        allow_empty=True,
        to_none_on_empty=False,
        special_null_keyword=None
        )
    # pyrefly: ignore  # bad-specialization
    if nombre and nombre.strip() != "" and nombre.strip() != cliente_existente[1].strip():
        #1. si el usuario ingreso un nombre (no esta vacio ni es none)
        #2. and el nuevo nombre es diferente al actual
        #3. and el nombre no es una cadena vacia (alow_empty=True y no queremos actualizar vacio)
        if check_client_name_exist(nombre, USER_ID): #volvemos a validar unicidad del nombre nuevo
            print(f"ERROR: el nombre '{nombre}' ya existe para tu usuario {sys_usr(USER_ID)}\nNo se actulizara el nombre\n") #no agregamos a updates{} si ya existe
        else:
            updates['nombre'] = nombre # -/- insertamos nombre en el diccionario -/-
        
    #Telefono
    #------------------------------------------------------------------
    telefono = clean_input(
        # pyrefly: ignore  # bad-specialization
        f"Nuevo telefono (actual: {cliente_existente[2] if cliente_existente[2] else 'N/A'}): (Deje vacio omitir, escriba 'NULL' para borrar)\n",
        min_len=0,
        max_len=10,
        allow_empty=True,
        to_none_on_empty=False, #retorna una cadena vacia "", no queremos retornar None
        special_null_keyword='NULL'
    )
    #Caso 1. El usuario quiere borrar el numero ingreso NULL
    if telefono is None: #validamos que el telefono, no esta vacio, no es None,
        updates['telefono'] = None # -/- insertamos None en el diccionario -/-
        print("Numero de Telefono Borrado\n")
    #Caso 2. El Usuario no ingreso nada (omitio el campo) o solo ingreso espacios
    elif telefono == "":
        print("Telefono no modificado\n")
        pass
    #Caso 3. El usuario ingreso un valor diferente a NULL y no vacio
    else:
        #primero verificamos que el  numero no sea igual
        # pyrefly: ignore  # bad-specialization
        if telefono.strip() == cliente_existente[2]:
            print(f"El numero {telefono} es el mismo que el actual\nNo se actualizo el telefono\n")
        #si no es igual validamos que sea un numero
        elif telefono.isdigit():
            updates['telefono'] = telefono 
            print(f"Numero de Telefono Actualizado a {telefono}\n")
        else:
            #esto es solo si no es NULL, vacio, no es igual, y no es solo digitos
            print(f"WARN: El numero ingresado {telefono}\nNo se actualizo el telefono\n")


    #Ubicacion
    #----------------------------------------------------------------------------
    ubicacion = clean_input(
        # pyrefly: ignore  # bad-specialization
        f"Nueva ubicacion aproximada (actual: {cliente_existente[3] if cliente_existente[3] else 'N/A'})\n",
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
        f"URL de la foto (actual: {cliente_existente[4] if cliente_existente[4] else 'N/A'})\n",
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
        f"Nuevo comentario (actual: {cliente_existente[5] if cliente_existente[5] else 'N/A'})\n",
        allow_empty=True,
        to_none_on_empty=False,
        special_null_keyword='NULL'
    )
    if comentario is not None and comentario != "":
        updates["comentario"] = comentario
    elif comentario is None: #si el usuario escribio NULL
        updates["comentario"] = None
    
    #------------------------------------------------------------------------------------
    
    #si no hay cambios ingresados
    if updates: #Si el diccionario NO esta vacio
        if client_update(client_id, USER_ID, **updates):
            print(f"Cliente actualizado con exito")
            list_client(client_id, USER_ID)
        else:
            print("No se pudo actualizar el cliente")
    else: #si no hay datos almacenados en updates{}
        print("No se ingresaron datos para actualizar\nOperacion cancelada\n")
        list_client(client_id, USER_ID)

#////---- Funcion para actualizar saldo del cliente ----////
def manejo_saldo():
    """Manejo de la logica para modifica saldo del cliente"""
    print("\n---ACTUALIZANDO SALDO DE CLIENTE---\n")
    busqueda() #mostramos los clientes para que el usuario sepa que ID elegir
    client_id = validar_cliente()
    print(f"SALDO ACTUAL")
    # list_client(client_id, USER_ID)

    #solicitamos el monto a restar o sumar y toca validarlo
    while True:
        monto_str = input("\nIngrese el monto\npara añadir saldo solo escriba el monto seguido de 2 decimales\nEj: 00.00\npara restar al saldo escriba el signo '-' seguido del monto\nEj: -00.00\n\n")
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
def manejo_delete() -> None:
    """Manejo de la logica para eliminar clientes"""
    print("\n---ELIMINANDO CLIENTE---\n")
    print("\n---VERIFIQUE DOS VECES EL CLIENTE A ELIMINAR---\n")
    busqueda() #mostramos los clientes para que el usuario sepa que ID elegir
    client_id, cliente_existente = validar_cliente()
    #confirmamos si el cliente es correcto
    # pyrefly: ignore  # bad-specialization
    print(f"Datos del cliente seleccionado: ID: {client_id}, Nombre: {cliente_existente[1]}, Telefono: {cliente_existente[2]}, Ubicacion: {cliente_existente[3]}, Saldo: {cliente_existente[7]}")
    
    while True:
        # pyrefly: ignore  # bad-specialization
        confirmacion = input(f"Seguro que desea eliminar el cliente con ID: {client_id} (Nombre{cliente_existente[1]})\n//--   S/N   --//\n").strip().upper()
        if confirmacion == 'N':
            print("Omitiendo eliminacion -- Operacion cancelada\n---   NO SE ELIMINARON DATOS  ---")
            break
        elif confirmacion == 'S':
            if eliminar_cliente(client_id, USER_ID): #llamamos a la funcion para eliminar, si retona True se ejecuta lo siguiente
                # pyrefly: ignore  # bad-specialization
                print(f"SE ELIMINO EL CLIENTE CON ID: {client_id} (Nombre: {cliente_existente[1]})")
                break
            else:
                print("ERROR: No se pudo eliminar el cliente")
                break
        else: # si ingresan algo diferente a S o N
            print("Entrada Invalida, ingrese S para eliminar o N para cancelar\n")






if __name__ == "__main__":

    main_cli()
    