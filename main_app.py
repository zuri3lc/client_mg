#////////------- IMPORTS ---------//////
from db.operations import (
    crear_tabla_clientes,
    agregar_cliente,
    obtain_clients,
    client_update,
    eliminar_cliente
)


#####-------//////INICIO DE LA LOGICA DE PRUEBA/////--------######
#Establecemos los id del usuario actual fijo temporalmente
ID_USUARIO_ACTUAL = 1
ID_2_PRUEBA = 2

def crud_test():
    """
    FUNCION PRINCIPAL QUE EJECUTA TODAS LAS PRUEBAS DEL CRUD
    """
    print('--- /// EJECUTANDO CONFIG INICIAL Y PRUEBAS DE CRUD /// ---')

    #1 asegurarnos que la tabla exista
    if crear_tabla_clientes():
        print("\nPRUEBA DE CREACION Y MANEJO DE DUPLICADOS\n")
        print("AGREGANDO CLIENTES DE PRUEBA PARA EL USUARIO 1")

        #insertamos unos usuarios de prueba
        agregar_cliente("Juan Perez", "C 12 #32", "5544332233", "foto_juan.png", "Cliente Nuevo", ID_USUARIO_ACTUAL) #valido 1
        agregar_cliente("Maria Garcia", "C 123 #252", "1122334455", "foto_maria.png", "Al Corriente", ID_USUARIO_ACTUAL) #valido 2
        agregar_cliente("Carlos Lopez", "C Juana #1534", "9900220011", "foto_carlos.png", "Cuenta Atrasada", ID_USUARIO_ACTUAL) #valido 3
        agregar_cliente("Zuriel Canche", "C 118a #921", "9992506511", "foto_z.png", "Al Corriente", ID_USUARIO_ACTUAL)#valido 4

        print(f"INSERTANDO UN USUARIO DUPLICADO PARA EL ID DE USUARIO {ID_USUARIO_ACTUAL}")
        agregar_cliente("Zuriel Canche", "C 118a #999", "9991226511", "foto_a.png", "Moroso", ID_USUARIO_ACTUAL) #----INVALIDO---- 1

        print(f"AGREGANDO USUARIO DUPLICADO PARA EL ID DE USUARIO {ID_2_PRUEBA}")
        agregar_cliente("Zuriel Canche", "C Malla #51", "3923743462", "foto_6.png", "Cliente Nuevo", ID_2_PRUEBA) #valido 5

        print(f"AGREGANDO USUARIO DIFERENTE PARA EL ID DE USUARIO {ID_USUARIO_ACTUAL}")
        agregar_cliente("Lola Bunny", "C 18a #121", "8934651243", "foto_l.png", "Al Corriente", ID_USUARIO_ACTUAL) #valido 6

        print("\n---PRUEBAS DE LECTURA SELECT---\n")
        print(f"Obteniendo y mostrando clientes del usuario ID {ID_USUARIO_ACTUAL}...")
        clientes_usuario_1 = obtain_clients(ID_USUARIO_ACTUAL)
        if clientes_usuario_1:
            print(f"Total de clientes para el usuario {ID_USUARIO_ACTUAL}...\n{len(clientes_usuario_1)}")
        else:
            print(f"No se encontraron clientes para el usuario ID {ID_USUARIO_ACTUAL}")
        #--obteniendo usuarios del sistem_user2
        print(f"Obteniendo y mostrando clientes del usuario ID {ID_USUARIO_ACTUAL}...")
        clientes_usuario_2 = obtain_clients(ID_2_PRUEBA)
        if clientes_usuario_2:
            print(f"Total de clientes para el usuario {ID_2_PRUEBA}...\n{len(clientes_usuario_2)}")
        else:
            print(f"No se encontraron clientes para el usuario ID {ID_2_PRUEBA}")

        print("---PRUEBAS DE ACTUALIZACION (UPDATE)---")
        print("Actualizando status cliente 'Carlos Lopez'")
        client_update(3, ID_USUARIO_ACTUAL, comentario="Comentario de prueba")

        print("actualizando un cliente que no le pertenece")
        client_update(5, ID_USUARIO_ACTUAL, comentario="actualizando cliente de no pertenencia")


        print("actualizando un cliente inexistente")
        client_update(999, ID_USUARIO_ACTUAL, comentario="actualizando cliente inexistente")

        print("Actualizando cliente generando un duplicado")
        client_update(6, ID_USUARIO_ACTUAL, nombre="Zuriel Canche")

        print("//---VERIFICANDO CLIENTES DESPUES DE LA ACTUALIZACION---//")
        obtain_clients(ID_USUARIO_ACTUAL)
        obtain_clients(ID_2_PRUEBA)

        print("\n//---PRUEBAS DE ELIMINACION (DELETE)---//")
        print("ELIMINANDO CARLOS LOPEZ ID 3 USER 1")
        eliminar_cliente(3, ID_USUARIO_ACTUAL)

        print("ELIMINANDO CLIENTE INEXISTENTE")
        eliminar_cliente(999, ID_USUARIO_ACTUAL)
        
        print("ELIMINANDO CLIENTE SIN PROPIEDAD")
        eliminar_cliente(5, ID_USUARIO_ACTUAL)

        print("VERIFICANDO CLIENTES DESPUES DE LA ELIMINACION")
        obtain_clients(ID_USUARIO_ACTUAL)
        obtain_clients(ID_2_PRUEBA)
    else:
        print("NO SE PUEDE INICIALIZAR LA DB, NO SE REALIZARON CAMBIOS")
#  /////--------aqui termina la funcion de prueba---------////////

if __name__ == "__main__":
    crud_test()
    # ////----con esta linea llamamos a la funcion que creamos----////