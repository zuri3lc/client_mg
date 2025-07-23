# app/auth.py
# Este módulo se encarga exclusivamente de la autenticación de usuario
import getpass
from .database import (
    verificar_credenciales_db,
    registrar_usuario_db,
    check_username_exist_db
)
from .utils import (
    clean_input
)
from .user_interface import (
    get_username_by_id_db
)

# MANEJO DEL LOGIN
def manejar_login():
    """Pide las credenciales al usuario y las valida"""
    print("\n--- INICIO DE SESION ---\n\n")
    username = input("Ingrese su nombre de usuario: \n").strip()
    # pedimos la contraseña de forma segura usando getpass
    password = getpass.getpass("Ingrese su contraseña: \n")
    #validamos las credenciales
    user_id = verificar_credenciales_db(username, password)
    
    if user_id is not None: #si la consulta no devuelve None
        #print(f"\n--- Bienvenido {sys_usr(user_id).upper()} ---\n") #type: ignore
        return user_id #retornamos el id del usuario
    else:
        print("\n--- ERROR ---\n--- Nombre de usuario o contraseña incorrecta ---\n")
        return None #retornamos None si las credenciales son invalidas


# MANEJO DEL REGISTRO DE USUARIOS
def manejar_registro():
    """Pide los datos para un nuevo usuario y lo registra"""
    print("\n--- REGISTRO DE NUEVO USUARIO ---\n")
    while True:
        username = clean_input(
            "Ingrese un nombre de usuario (min 5 caracteres, max 50): \n",
            min_len=5,
            max_len=50,
            allow_empty=False
        )
        #verificamos que el nombre de usuario no exista
        if username is False: #si retorna false por algun motivo brincamos el resto del bucle
            continue
        if check_username_exist_db(username):
            print(f" ERROR: el nombre de usuario '{username}' ya existe\n")
            continue
        else:
            break
    #pedimos la contraseña de forma segura usando getpass
    password = getpass.getpass("Ingrese una contraseña (min 6 caracteres): \n")
    #confirmacion de la contraseña
    password_confirm = getpass.getpass("Confirme su contraseña: \n")
    
    #verificamos que sean iguales
    if password != password_confirm:
        print("\n--- ERROR ---\n--- Las contraseñas no coinciden ---\n")
        return
    if len(password) < 6:
        print("\n--- ERROR ---\n--- La contraseña debe tener al menos 6 caracteres ---\n")
        return
    nombre = clean_input(
        "Ingrese su nombre completo (min 3 caracteres, max 255) (Deje vacio para omitir): \n",
        min_len=3,
        max_len=255,
        allow_empty=True
    )
    user_data = registrar_usuario_db(
        username=username,
        password=password,
        nombre=nombre if nombre else None,  # si el nombre esta vacio lo dejamos None
    )
    
    if user_data:
        print(f"\n--- Usuario registrado exitosamente ---\n")
        print(f"--- Bienvenido {get_username_by_id_db(user_data)} ---\n")
        return user_data
    else:
        print("\n--- ERROR ---\n--- No se pudo registrar el usuario ---\n")
        return None



