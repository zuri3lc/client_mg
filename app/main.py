# app/main.py
# Este archivo es el corazón de la aplicación, el orquestador.
# No contiene lógica de base de datos ni de interfaz de usuario directamente,
# solo llama a las funciones de otros módulos.
#////////------- IMPORTS ---------//////
from ast import Break
from ast import Continue
from ast import Return
import getpass #getpass para manejar contraseñas
from app.database import (
    crear_tablas,
)
from app.auth import (
    manejar_login,
    manejar_registro
)
from app.client_management import (
    crear_nuevo_cliente,
    gestionar_actualizacion_saldo,
    actualizar_cliente,
    busqueda,
    ver_clientes,
    gestionar_eliminacion_cliente,
    manejo_historial,
    gestionar_actualizacion_estado
)
from app.user_interface import (
    mostrar_menu_principal
)
from datetime import date #fecha
from decimal import Decimal, InvalidOperation #decimal para uso con saldos

#////---- Funcion principal de la CLI ----////
def main_cli():
    """Funcion principal, maneja el flujo de la aplicacion"""
    if not crear_tablas():
        print("\n-/- ERROR -/-")
        print("-/-NO SE PUDO INICIALIZAR LA BASE DE DATOS-/-/")
        print("-/-/-SALIENDO-/-/\n\n")
        return
    
    usuario_actual_id = None #inicializamos el id del usuario actual como None
    
    while True:
        if usuario_actual_id is None: #mientras no tengamos un usuario logueado
            print("\n--- BIENVENIDO ---\n")        
            print("| 1. Iniciar Sesion\n| 2. Registrar nuevo Usuario\n| 3. Salir\n\n")
            print('-' * 40)
            opcion_auth = input("Ingrese una opcion: 1 - 3\n").strip()
            
            if opcion_auth == "1": #opcion de iniciar sesion
                usuario_actual_id = manejar_login() #llamamos a la funcion de login
            elif opcion_auth == "2": #opcion de registro
                usuario_actual_id = manejar_registro() #llamamos a la funcion de registro
            elif opcion_auth == "3": #opcion de salir
                print("\nSALIENDO DEL PROGRAMA...\n")
                break #salimos del programa
            else: #opcion invalida
                print("\n--OPCION NO VALIDA--\n--INGRESE UN NUMERO DEL 1 AL 3--\n")            
            #si llegamos aqui, tenemos un usuario logueado
        else:
            #Menu principal
                mostrar_menu_principal(usuario_actual_id) #mostramos el menu
                opcion = input("\n| Ingrese una opcion: 1 - 8\n").strip()
                
                if opcion == '1':
                    crear_nuevo_cliente(usuario_actual_id)
                elif opcion == '2':
                    ver_clientes(usuario_actual_id)
                elif opcion == '3':
                    gestionar_actualizacion_saldo(usuario_actual_id)
                elif opcion == '4':
                    actualizar_cliente(usuario_actual_id)
                elif opcion == '5':
                    busqueda(usuario_actual_id)
                elif opcion == '6':
                    manejo_historial(usuario_actual_id)
                elif opcion == '7':
                    gestionar_actualizacion_estado(usuario_actual_id)
                elif opcion == '8':
                    gestionar_eliminacion_cliente(usuario_actual_id)
                elif opcion == '9':
                    print("\nCERRANDO SESION...\nHasta luego!\n")
                    usuario_actual_id = None #cerramos la sesion e iniciamos de nuevo
                else:
                    print("--OPCION NO VALIDA--\n--NGRESE UN NUMERO DEL 1 AL 8--\n")

if __name__ == "__main__":
    
    """Punto de entrada principal del programa"""
    try:
        main_cli() #llamamos a la funcion principal
    except KeyboardInterrupt: #capturamos Ctrl+C para salir del programa
        print("\n\nSALIENDO DEL PROGRAMA...\n")
    except Exception as e: #capturamos cualquier otro error inesperado
        print(f"\n Ocurrio un error inesperado: {e}\n Saliendo del programa...\n")
        import sys
        sys.exit(1) #salimos con codigo de error 1
    finally:
        print("\n=== PROGRAMA FINALIZADO ===\n")

