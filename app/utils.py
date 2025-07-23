#app/utils.py --- modulo de funciones de utilidad

# ==> Nuestro Contrato de Columnas para Clientes:
# ==> Índice 0: id
# ==> Índice 1: nombre
# ==> Índice 2: telefono
# ==> Índice 3: ubicacion_aproximada
# ==> Índice 4: foto_domicilio
# ==> Índice 5: comentario
# ==> Índice 6: fecha_adquisicion
# ==> Índice 7: fecha_ultima_modificacion
# ==> Índice 8: saldo_actual
# ==> Índice 9: estado_cliente
# ==> Índice 10: usuario_sistema_id

# ==> Nuestro Contrato de Columnas para Movimientos:
# ==> Índice 0: mv.id
# ==> Índice 1: mv.fecha_movimiento
# ==> Índice 2: mv.tipo_movimiento
# ==> Índice 3: mv.monto
# ==> Índice 4: mv.saldo_anterior
# ==> Índice 5: mv.saldo_final
# ==> Índice 6: c.nombre

#---- FUNCION PARA LIMPIAR Y PROCESAR ENTRADAS DE USUARIO ----
def clean_input(promt, min_len=0, max_len=255, allow_empty=True, to_none_on_empty=False, special_null_keyword=None):
    """SOLICITA UNA ENTRADA AL USUARIO, LA LIMPIA Y LA VALIDA"""
    while True:
        user_input = input(promt).strip() #elimina los espacios vacios al principio y al final
        
        #convertimos a None si se usa la palabra clave
        if special_null_keyword and user_input.upper() == special_null_keyword.upper():
            return None
        
        #entrada vacia
        if not user_input:
            if allow_empty: #si se permite vacio convertimos a None
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

#funcion para obtener un id de cliente valido
def obtener_client_id():
    while True:
        try:
            client_id_str = input("\n Ingrese el ID del cliente seleccionado: \n")
            client_id = int(client_id_str)
            if client_id <= 0: #validamos que mayor a cero
                print("\n El ID no puede ser negativo o cero. Intente de nuevo.\n")
            else:
                return client_id
        except ValueError: #atrapamos el error si no es un numero y reinciamos el bucle
            print(" Entrada invalida. Por favor, ingrese un numero entero para el ID.\n")

