# conectar la base de datos
#from asyncio.exceptions import LimitOverrunError
import psycopg #importamos la libreria para 'hablar' con la DB
from datetime import date #esto es para la fecha de adquisicion
from psycopg.errors import UniqueViolation, ForeignKeyViolation # importamos el error especifico
from decimal import Decimal #importamos decimal para uso con saldos
import logging
import bcrypt


#-------configuracion de la conexion a PostgreSQL----------
# --Datos de la BD--
DB_NAME = "clients_db"
DB_USER = "gestor_clientes"
DB_PASSWORD = "RettkeStysi@k208"
DB_HOST = "192.168.1.113"
DB_PORT = "5433"
#-------------///////BLOQUE DE CONEXION A LA DB///////--------------------------
#-- CADENA DE CONEXION (esta linea conecta a la base de datos) --
conn_string = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

#---------------/////////////////CONFIGURACION LOGGER///////////------------------
logging.basicConfig(
    level=logging.INFO, #definimos la severidad del log
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', #define el formato del log
    handlers=[
        logging.FileHandler("app_log.log"), #guarda los logs en el archivo app_log.log
        #logging.StreamHandler() #imprime los logs en la consola
    ]
)
logger = logging.getLogger(__name__) #creamos un logger para este modulo

#---------------/////////////////EMPIEZA DEFINICION DE FUNCIONES///////////------------------
#----------------------//////FUNCIONES/////-------------------

#  ESTABLECE UNA CONEXION A LA DB
def db_conection():
    """
    ESTABLECE Y DEVUELVE UNA NUEVA CONEXIÓN A LA DB
    """
    try:
        conn = psycopg.connect(conn_string) #nos conectamos a la DB
        logger.info("Conexion a la DB establecida con exito")
        return conn
    except psycopg.Error as e: # 'atrapamos' los errores y los guardamos en una variable llamada e
        logger.critical(f"ERROR AL CONECTAR A LA DB: {e}")
        return None #terminamos la conexión nueva

#  CREACION DE LAS TABLAS DE LA DB
def crear_tablas():
    """
    CONECTAMOS LA BASE DE DATOS Y CREAMOS LA TABLA CLIENTES Y MOVIMIENTOS
    Retorna True si todo sale bien, False si hay algun error
    """
    conn = db_conection()
    if conn is None: #definimos que si hubo un error al tratar de conectar nos devuelva
        return False #No se pudo establecer la conexion
    
    cur = None #esta la variable cursor, asi nos aseguramos que siempre existan

    try:
        cur = conn.cursor()
        
        # ---------------- TABLA USUARIOS DEL SISTEMA ----------------
        create_usuarios_sql = """
        CREATE TABLE IF NOT EXISTS usuarios(
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL, -- restriccion de unicidad
            password_hash VARCHAR(255) NOT NULL,
            nombre VARCHAR(255),
            fecha_creacion DATE NOT NULL DEFAULT CURRENT_DATE
        );
        """
        
        # ---------------- TABLA CLIENTES ----------------
        create_clientes_sql = """
        CREATE TABLE IF NOT EXISTS clientes(
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            telefono VARCHAR(50),
            ubicacion_aproximada TEXT,
            foto_domicilio VARCHAR(255),
            comentario TEXT,
            fecha_adquisicion DATE NOT NULL DEFAULT CURRENT_DATE,
            fecha_ultima_modificacion DATE NOT NULL DEFAULT CURRENT_DATE,
            saldo_actual NUMERIC(10, 2) DEFAULT 0.00,
            estado_cliente VARCHAR(50) DEFAULT 'regular',
            usuario_sistema_id INTEGER NOT NULL,
            CONSTRAINT uq_nombre_id_usuario UNIQUE (nombre, usuario_sistema_id),
            -- relacion con la tabla de usuarios del sistema
            CONSTRAINT fk_usuario_sistema FOREIGN KEY (usuario_sistema_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
        """     #restriccion al final de la sentencia
                # uq_nombre_id_usuario restriccion de unicidad para evitar duplicados el nombre del cliente y el id del usuario del sistema
                #fk_usuario_sistema relaciona la tabla clientes con la tabla usuarios del sistema
            
        # ----------------- TABLA MOVIMIENTOS -----------------
        create_movimientos_sql = """
        CREATE TABLE IF NOT EXISTS movimientos(
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER NOT NULL,
            fecha_movimiento DATE NOT NULL DEFAULT CURRENT_DATE,
            tipo_movimiento VARCHAR(50) NOT NULL CHECK (tipo_movimiento IN ('deuda_inicial', 'abono', 'actualizacion')),
            monto NUMERIC(10, 2) NOT NULL,
            saldo_anterior NUMERIC(10, 2) NOT NULL,
            saldo_final NUMERIC(10, 2) NOT NULL,
            usuario_sistema_id INTEGER NOT NULL,
            CONSTRAINT fk_cliente_movimiento FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        );
        """ # fk_cliente_movimiento relaciona la tabla movimientos con la tabla clientes
        
        logger.info("INTENTANDO CREAR TABLA 'USUARIOS'...")
        cur.execute(create_usuarios_sql) 
        
        logger.info("INTENTANDO CREAR TABLA 'CLIENTES'...")
        cur.execute(create_clientes_sql) 
        
        logger.info("INTENTANDO CREAR TABLA 'MOVIMIENTOS'...")
        cur.execute(create_movimientos_sql)
        
        conn.commit() #hacemos 'commit' o guardamos los cambios de forma permanente
        logger.info("TABLAS CREADAS EXITOSAMENTE O YA EXISTENTE...")
        return True #indicamos que fue exitoso

    except psycopg.Error as e:
        logger.error(f"/// ERROR AL CONECTAR O CREAR LAS TABLAS: {e} ///")
        if conn:
            conn.rollback()
        return False
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            logger.info("/// CONEXION A LA BASE DE DATOS CERRADA ///")

def registrar_usuario(username, password, nombre=None):
    """
    Registra un nuevo usuario en la base de datos.
    """
    #pasos..
    # 1. Hashear la contraseña
    # - password.encode('utf-8') convierte la contraseña de string a bytes
    #2 - bcrypt.gensalt() genera una sal aleatorio para hacer el hash mas seguro
    #3 - bcrypt.hashpw() aplica el hash a la contraseña y la sal, creando un hash seguro
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    conn = db_conection() #conectamos a la DB
    if conn is None: #si hay problemas con la conexion
        return False #devolvemos False
    
    cur = None
    try:
        cur = conn.cursor()
        insert_sql = """
        INSERT INTO usuarios (
            username,
            password_hash,
            nombre)
        VALUES (
            %s, %s, %s)
        RETURNING id;
        """
        cur.execute(insert_sql, (username, password_hash.decode('utf-8'), nombre)) 
        user_id = cur.fetchone()[0] #type: ignore
        conn.commit() #guardamos los cambios
        logger.info(f"Usuario '{username}' registrado con exito, ID: {user_id}")
        return user_id #devolver el ID del nuevo usuario
    except UniqueViolation:
        logger.warning(f"El usuario '{username}' ya existe, no se pudo registrar.")
        if conn:
            conn.rollback() #deshacemos los cambios si hubo un error
            return None #None indica que el usuario ya existe
    except psycopg.Error as e:
        logger.error(f"Error al registrar el usuario '{username}'\nDetalles: {e}")
        if conn:
            conn.rollback()
        return False #False error general de la DB
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# VERIFICA LAS CREDENCIALES DEL USUARIO
def verificar_credenciales(username, password):
    """
    Verifica las credenciales del usuario en la base de datos.
    Devuelve el ID del usuario si las credenciales son correctas, de lo contrario, devuelve None.
    """
    conn = db_conection()
    if conn is None:
        return None
    
    cur = None
    try:
        cur = conn.cursor()
        select_sql = """
        SELECT id, password_hash FROM usuarios WHERE username = %s;
        """
        cur.execute(select_sql, (username,)) #la coma es necesaria para que sea una tupla
        user_data = cur.fetchone() #obtenemos una fila de la consulta
        
        if user_data: #si hay datos
            user_id, password_hash = user_data
            #verificamos si la contraseña coincide con el hash almacenado
            # bcrypt.checkpw() compara la contraseña ingresada con el hash almacenado
            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                #checkpw => convertimos la contraseña a bytes y el hash a bytes y comparamos
                logger.info(f"Credenciales correctas {username} (ID: {user_id})")
                return user_id # PASS devolvemos el user_id
            else:
                logger.warning(f"Contraseña incorrecta para el usuario '{username}'")
                return None # None si la contraseña es incorrecta
        else:
            logger.warning(f"Usuario '{username}' no encontrado")
            return None # Usuario no encontrado
    except psycopg.Error as e:
        logger.error(f"Error al verificar las credenciales\nDetalles: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

#  DEFINE EL NOMBRE DEL USUARIO DE LA SESION ACTUAL
def sys_usr(usuario_sistema_id):
    """"
    DEVUELVE EL NOMBRE DEL USUARIO DEL SISTEMA
    """
    conn = db_conection()
    if conn is None:
        return None
    
    cur = None
    try:
        cur = conn.cursor()
        select_sql = """
        SELECT username FROM usuarios WHERE id = %s;
        """
        cur.execute(select_sql, (usuario_sistema_id,))
        resultado = cur.fetchone() #Type: ignore
        if resultado:
            return resultado[0].upper() #type: ignore
        else:
            return "Usuario Desconocido" # nombre por defecto si no se encuentra el usuario
    except psycopg.Error as e:
        logger.error(f"Error al obtener el nombre del usuario: {e}")
        return "Usuario Desconocido" # nombre por defecto si hay un error
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

#  VERIFICAMOS SI EL NOMBRE EXISTE EN LA DB
def check_client_name_exist(nombre, usuario_sistema_id):
    """
    El unico trabajo de esta funcion es verificar si el nombre del cliente ya existe en la DB ligado al usuario actual
    
    Args:
        nombre (str): El nombre del cliente a verificar
        usuario_sistema_id (int): El ID del usuario al que pertenece el cliente
    Returs:
        bool: True si el nombre existe, False en caso contrario
    """
    conn = db_conection()
    if conn is None:
        logger.error("No se pudo conectar a la DB")
        return False

    cur = None
    try:
        cur = conn.cursor()
        # usamos ILIKE para busqueda insensible de mayusculas y minusculas
        select_sql = """
        SELECT COUNT(*) FROM clientes
        WHERE TRIM(nombre) ILIKE TRIM(%s) AND usuario_sistema_id = (%s);
        """
        #la sentencia le dice que busque y seleccione en la tabla clientes todos las filas 
        # que encuente que sean iguales independiente de mayusculas y minusculas y 
        # pertenezcan al mismo usuario
        logger.info(f"Verficando si el nombre '{nombre}' ya existe para el usuario {usuario_sistema_id}")
        cur.execute(select_sql, (nombre, usuario_sistema_id))
        count = cur.fetchone()[0] #type: ignore
        #cur.fetchone solo devolvera 1 valor, porque en este caso tiene la directiva UNIQUE
        #ese valor lo tomamos con el indice 0 y se lo asignamos a la variable count
        
        if count > 0:
            logger.warning(f"El nombre {nombre} ya existe para el usuario {usuario_sistema_id}")
            return True #indica que si existe un duplicado
        else:
            logger.info(f"El nombre del cliente {nombre} es unico para el usuario {usuario_sistema_id}")
            return False #esto indica que no existe
    except psycopg.Error as e:
        logger.error(f"Error al verificar el nombre del cliente {nombre}: {e}")
        return True #indicamos que si existe aunque no sepamos, para evitar duplicados
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

#  AGREGAR CLIENTES
def agregar_cliente(nombre, telefono, ubicacion, foto_domicilio, comentario, saldo_incial, usuario_sistema_id
    ):
    """
    Agrega un nuevo cliente a la DB, sin duplicados por id
    """
    conn = db_conection() #conectamos a al DB
    if conn is None: #si hay problemas
        return False #devolvemos false
    
    cur = None
    try:
        cur = conn.cursor()
        
        # paso 1
        # insertar el cliente
        insert_sql = """
        INSERT INTO clientes (
            nombre,
            telefono,
            ubicacion_aproximada,
            foto_domicilio,
            comentario,
            fecha_adquisicion,
            saldo_actual,
            usuario_sistema_id
        ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id; -- OBTENEMOS EL id DEL CLIENTE INSERTADO
        """
        # con date.today() añadimos la fecha de adquisicion por defecto
        cur.execute(insert_sql, (
            nombre,
            telefono,
            ubicacion,
            foto_domicilio,
            comentario,
            date.today(),
            saldo_incial,
            usuario_sistema_id
        )) #aqui le pedimos al cursor que ejecute la sentencia sql, con los valores que le indicamos
        
        cliente_id = cur.fetchone()[0] # type: ignore
        
        #paso 2 insertamos el cliente si tiene saldo inicial
        if saldo_incial > 0:
            insertar_movimiento_sql = """
            INSERT INTO movimientos (
                cliente_id,
                tipo_movimiento,
                monto,
                saldo_anterior,
                saldo_final,
                usuario_sistema_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s)
            """
            cur.execute(insertar_movimiento_sql, (
                cliente_id,
                'deuda_inicial',
                saldo_incial, #en este contexto exclusivamente saldo_incial es lo mismo que saldo final
                0.00,
                saldo_incial,
                usuario_sistema_id
            ))
        
        conn.commit()
        user = sys_usr(usuario_sistema_id)
        logger.info(f'Cliente "{nombre}" ah sido agregado con exito, id: {cliente_id}')
        print(f'\nCliente "{nombre}" ah sido agregado con exito, id: {cliente_id}')
        return cliente_id # devuelve el id del nuevo cliente
    
    #----////CON ESTE BLOQUE CAPTURAMOS EL ERROR DE Unique.Violaton/////-----
    except UniqueViolation as e: # capturamos el error especifico de unicidad
        logger.warning(f"ERROR: El cliente '{nombre}' para el Usuario '{user}' ya existe, no se agrego.\nDetalle: \n {e}") # type: ignore
        if conn:
            conn.rollback() #el rollback es obligatorio para regresar la conexion a su estado original
        return False
    #----////AQUI CERRAMOS EL BLOQUE DE CAPTURA DEL ERROR Unique.Violaton/////-----
    
    except psycopg.Error as e: #manejo de errores si psycopg tiene algun error
        logger.error(f"Error al agregar cliente {nombre}: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

#  OBTENEMOS TODOS LOS CLIENTES DE UN USUARIO
def obtain_clients(usuario_sistema_id):
    """
    OBTIENE Y MUESTRA TODOS LOS CLIENTES DE UN USUARIO ESPECIFICO
    """
    conn = db_conection()
    if conn is None:
        return [] #Devuelve una lista vacia si hay algun problema con la conexion
    
    cur = None
    clientes = []
    try:
        user = sys_usr(usuario_sistema_id)
        cur = conn.cursor()
        # seleccionamos todas las columnas (*) y filtramos por usuario del sistema
        select_sql = "SELECT * FROM clientes WHERE usuario_sistema_id = %s ORDER BY ID;" #creamos una variable con la sentencia de busqueda
        cur.execute(select_sql, (usuario_sistema_id,)) #la comma es necesaria si solo hay un elemento en la tupla
        # ejecutamos la consulta y obtenemos los resultados
        logger.info(f"\nObteniendo clientes del usuario {user}")
        print(f"\nObteniendo clientes del usuario {user}")
        print("=" * 80) #imprimimos una linea de separacion
        clientes = cur.fetchall()
        
        if not clientes:
            logger.warning(f"No se encontraron clientes para el usuario {user}")
            print(f"No se encontraron clientes para el usuario {user}")
        else:
            logger.info(f"Se encontraron {len(clientes)} clientes para el usuario {user}")
            return clientes #retornamos la lista de clientes obtenidos

    except psycopg.Error as e:
        logger.error(f'Error al obtener clientes: {e}')
        return [] # regresamos a la lista vacia
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        #cerramos cursor y conexion

#  ACTUALIZAR UNA FILA/CLIENTE
def client_update(cliente_id, usuario_sistema_id, **kwargs):
    
    
    """
    ACTUALIZA LOS DATOS DE UN CLIENTE ESPECIFICO, FILTRADO POR SU ID Y EL ID DEL PROPIETARIO DEL CLIENTE
    utiliza **kwargs para recibir de forma flexible los campos

    Args:
        cliente_id (int): El ID del cliente a actualizar
        usuario_sistema_id (int): el ID del usuario al que pertenece el cliente
        **kwargs: argumentos que se pasan como par clave:valor
    Returns:
        bool: True si se actualizo con exito, False en caso contrario
    """
    # 1ro verificamos si se pasaron campos para actualizar
    if not kwargs:
        logger.info("No se proporcionaron datos para actualizar")
        print("--ADVERTENCIA-- No se proporcionaron datos para actualizar")
        return False
    
    conn = db_conection()
    if conn is None: #si la conexion falla, devoolvemos False
        return False
    
    cur = None
    try:
        user = sys_usr(usuario_sistema_id)
        cur = conn.cursor()
        #construimos dinamicamente la parte SET de la consulta SQL
        #set_clauses, sera una lista de cadenas ej: "telefono = %s", "comentario = %s" etc
        set_clauses = []
        #values sera una lista que guarde los valores correspondientes a los '%s'
        values = []

        #iteramos sobre el diccionario 'kwargs'
        for key, value in kwargs.items():
            set_clauses.append(f"{key} = %s") #añadimos a la lista set_clauses el valor key del diccionario
            values.append(value) #añadimos el valor del diccionario a la lista values
        
        #ahora unimos las clausulas SET con comas para formar la parte SET de la sentencia SQL
        #ej- "telefono = %s, comentario = %s"
        set_sql = ",".join(set_clauses) #construimos la sentencia sql con la lista set_caluses

        #añadir el id del usuario y del cliente al final de la lista
        #cuando armemos las clausulas iran al final
        values.append(cliente_id)
        values.append(usuario_sistema_id)
        
        #armamos la sentencia
        update_sql = f"""
        UPDATE clientes
        SET {set_sql}
        WHERE id = %s AND usuario_sistema_id = %s; -- con esto aseguramos que el usuario del sistema, solo pueda editar sus propios clientes
        """

        #ejecutamos la consulta, pero hay que convertir los valores en values a una tupla, porque execute espera una tupla
        # pyrefly: ignore  # bad-argument-type
        cur.execute(update_sql, tuple(values))

        #cur.rowcount para obtener las filas afectadas
        if cur.rowcount > 0:
            conn.commit() #guardamos
            logger.info(f"Cliente con id {cliente_id} (usuario {user}) actualizado")
            print(f"Cliente con id {cliente_id} (usuario {user}) actualizado")
            return True
        else:
            conn.rollback() #si no funciona, deshacemos
            logger.warning(f"Cliente con id {cliente_id} (usuario {user}) no se encontro o no se realizaron cambios")
            print(f"Cliente con id {cliente_id} (usuario {user}) no se encontro o no se realizaron cambios")
            return False
    except UniqueViolation as e:
        #capturamos si se intenta crear un duplicado nombre/usuario_sistema_id
        logger.warning(f"--ERROR--\nNo se pudo actualizar cliente con ID {cliente_id}, la combinacion Nombre/Usuario ya existe")
        print(f"--ERROR--\nNo se pudo actualizar cliente con ID {cliente_id}, la combinacion Nombre/Usuario ya existe")
        if conn:
            conn.rollback()
        return False
    except psycopg.Error as e:
        logger.error(f"--ERROR--\nNo se pudo actualizar el cliente con ID {cliente_id} (general ERROR): {e}")
        print(f"--ERROR--\nNo se pudo actualizar el cliente con ID {cliente_id} (general ERROR): {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

#  ACTUALIZAR SALDOS
def actualizar_saldo(cliente_id, usuario_sistema_id, monto):
    """
    ACTUALIZA EL SALDO DE UN CLIENTE ESPECIFICO, FILTRADO POR SU ID Y EL ID DEL PROPIETARIO DEL CLIENTE

    Args:
        cliente_id (int): El ID del cliente a actualizar.
        usuario_sistema_id (int): el ID del usuario al que pertenece el cliente.
        monto (Decimal): El saldo a sumar si es positivo, restar si es negativo.
        returs:
            bool: True si se actualizo con exito, False en caso contrario
    """
    conn = db_conection()
    if conn is None:
        return False
    
    cur = None
    try:
        cur = conn.cursor()
        
        # Paso 1: obtener el saldo actual del cliente
        obtener_saldo_sql = """
        SELECT saldo_actual FROM clientes WHERE id = %s AND usuario_sistema_id = %s;
        """
        
        cur.execute(obtener_saldo_sql, (
            cliente_id,
            usuario_sistema_id))
        
        resultado = cur.fetchone()
        
        if not resultado:
            logger.warning(f"Cliente con ID {cliente_id} no encontrado")
            return False
        
        saldo_anterior = resultado[0] #type: ignore
        saldo_final = saldo_anterior + monto
        
        # Paso 2: Actualizar saldo del cliente
        actualizar_saldo_sql = """
        UPDATE clientes
            SET 
                saldo_actual = %s,
                fecha_ultima_modificacion = %s
        WHERE id = %s AND usuario_sistema_id = %s;
        """
        
        cur.execute(actualizar_saldo_sql, (
            saldo_final,
            date.today(), #actualizamos la fecha de ultima modificacion
            cliente_id,
            usuario_sistema_id))
        
        # Paso 3: Determinar el tipo de movimiento
        if monto > 0:
            tipo_movimiento = 'actualizacion' # agregar deuda
        else:
            tipo_movimiento = 'abono' # pagar deuda
            
        # Paso 4: registrar el movimiento
        registrar_movimiento_sql = """
        INSERT INTO movimientos (
            cliente_id,
            tipo_movimiento,
            monto,
            saldo_anterior,
            saldo_final,
            usuario_sistema_id
        ) VALUES (
            %s, %s, %s, %s, %s, %s
        )
        """
        
        cur.execute(registrar_movimiento_sql, (
            cliente_id,
            tipo_movimiento,
            monto,
            saldo_anterior,
            saldo_final,
            usuario_sistema_id
        ))
        
        conn.commit() #guardamos los cambios

        user = sys_usr(usuario_sistema_id)
        
        if cur.rowcount > 0:
            conn.commit() #guardamos cambios
            logger.info(f"Saldo cliente ID {cliente_id} (usuario {user}) actualizado) con {saldo_final}")
            #print(f"\nSaldo del cliente actualizado")
            return True
        else:
            conn.rollback() #si no se puede devolvemos al estado inicial
            logger.warning(f"No se pudo actualizar el saldo del cliente con ID {cliente_id} (usuario {user})")
            print(f"No se pudo actualizar el saldo del cliente con ID {cliente_id} (usuario {user})")
            list_client(cliente_id, usuario_sistema_id)
            return False
    except psycopg.Error as e:
        logger.error(f"ERROR al actualizar el saldo del cliente con ID {cliente_id} (general ERROR): {e}")
        print(f"ERROR al actualizar el saldo del cliente con ID {cliente_id} (general ERROR): {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            logger.info("/// CONEXION A LA BASE DE DATOS CERRADA ///")

#  LISTAR UN SOLO CLIENTE
def list_client(cliente_id, usuario_sistema_id):
    while True:
        conn = db_conection()
        if conn is None:
            return None #Devuelve None si hay algun problema con la conexion
        
        cur = None
        try:
            user = sys_usr(usuario_sistema_id)
            cur = conn.cursor()
            
            #seleccionamos la columna y la fila
            select_sql = "SELECT * FROM clientes WHERE id = %s AND usuario_sistema_id = %s;"
            cur.execute(select_sql, (cliente_id, usuario_sistema_id))

            encontrado = cur.fetchone()
            if encontrado:
                logger.info(f"\nCliente ID {cliente_id} listado con exito")
                print('=' * 80)
                print(" " * 30, "DETALLES DEL CLIENTE")
                print('=' * 80)
                print(f"| ID: {encontrado[0]}\n| Nombre: {encontrado[1]}\n| Telefono: {encontrado[2]}\n| Fecha de creacion: {encontrado[6]}\n| Ultima modificacion: {encontrado[7]}\n| Saldo: ${encontrado[8]}\n| Estado: --{encontrado[9].upper()}--")
                print('=' * 80)
                return encontrado # RETORNA EL CLIENTE ENCONTRADO Y SALE DEL BUCLE
            else:
                logger.warning(f"\nNo se encontraron datos para el ID {cliente_id} (usuario {user})")
                # print("No se encontraron datos para ese ID, intenta de nuevo.")
                return None #retornamos None para indicarle que no se encontro el id
        except (Exception, psycopg.Error) as e:
            logger.error(f"ERROR al listar el cliente con ID {cliente_id} (general ERROR): {e}")
            print(f"ERROR, no se puede conectar ni consultar con la DB\n")
            return None # Sale del bucle en caso de error de DB
        finally:
            if conn:
                conn.close()
            if cur:
                cur.close()

#  ELIMINAR CLIENTES
def eliminar_cliente(cliente_id, usuario_sistema_id):
    """
    ELIMINA UN CLIENTE ESPECIFICO BASANDOSE EN SU ID Y EL ID USUARIO PROPIETARIO

    Args:
        cliente_id (int): El ID del cliente a actualizar
        usuario_sistema_id (int): el ID del usuario al que pertenece el cliente
    Returns:
        bool: True si se actualizo con exito, False en caso contrario
    """

    #conectamos a la db
    conn = db_conection()
    if conn is None:
        return False
    
    cur = None
    try:
        user = sys_usr(usuario_sistema_id)
        cur = conn.cursor()
        #armamos la sentencia añadiendo ambos IDs a la clausula para asegurar que solo el propietario pueda eliminar
        delete_sql = "DELETE FROM clientes WHERE id = %s AND usuario_sistema_id = %s;"
        cur.execute(delete_sql, (cliente_id, usuario_sistema_id))

        #cur.rowcount para saber cuantas lineas fueron afectadas
        #si es > 0 significa que al menos una fila fue eliminada
        if cur.rowcount > 0:
            conn.commit() #solo guardamos si rowcount nos confirma que se elemino alguna fila
            logger.info(f"Cliente con ID: {cliente_id} (Usuario: {user}) eliminado con exito")
            print('=' * 80)
            print(f"Cliente con ID: {cliente_id} (Usuario: {user}) eliminado")
            print('=' * 80)
            return True
        else:
            conn.rollback() #si el rowcount es 0, el cliente no se encontro o no existe y deshacemos
            logger.warning(f"Cliente con ID {cliente_id} (Usuario {user}) no encontrado")
            print(f"\n---ERROR---\nCliente con ID {cliente_id} (Usuario {user}) no encontrado")
            return False
    except ForeignKeyViolation as e:
        #capturamos el error si el cliente esta en otra tabla
        logger.error(f"ERROR de clave foranea al eliminar cliente con ID {cliente_id}.\nDetalle\n{e}")
        print(f"\nNo se pudo eliminar cliente con ID {cliente_id}, debido a deoendencia en otra tabla.\nDetalle\n{e}")
        if conn:
            conn.rollback()
            return False
    except psycopg.Error as e:
        logger.error(f"ERROR general el eliminar cliente ID {cliente_id}.\n(GENERAL - ERROR)\n{e}")
        print(f"\nERROR al eliminar cliente con ID {cliente_id}.\n(GENERAL - ERROR)\n{e}")
        if conn:
            conn.rollback()
            return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

#  BUSQUEDA DE CLIENTES
def client_search(nombre_buscado, usuario_sistema_id):

    # Bucle principal para permitir múltiples búsquedas o salir
    while True: # Bucle para repetir la búsqueda si no hay resultados
        while True:
            nombre_buscado_limpio = nombre_buscado.strip()
            if not nombre_buscado_limpio:
                logger.warning("Intento de busqueda con nombre cliente vacio")
                print("-ERROR- El nombre a buscar no puede estar vacio")
                nombre_buscado = input("Ingrese el nombre a buscar: ")
            else:
                break

        conn = db_conection()
        if conn is None:
            return False
        
        cur = None

        # Bloque try-except para manejar errores durante la ejecución de la consulta
        try:
            cur = conn.cursor()
            sql_search = """
                SELECT 
                    id, -- 0
                    nombre, -- 1
                    telefono, -- 2
                    ubicacion_aproximada, -- 3
                    foto_domicilio, -- 4
                    comentario, -- 5
                    fecha_adquisicion,  -- 6
                    fecha_ultima_modificacion,  -- 7
                    saldo_actual, -- 8
                    estado_cliente, -- 9
                    usuario_sistema_id -- 10
                FROM clientes
                WHERE TRIM(nombre) ILIKE TRIM(%s) AND usuario_sistema_id = (%s);
                """
            patron_busqueda = f"%{nombre_buscado.strip()}%"
            logger.info(f"Buscando clientes con nombre '{nombre_buscado_limpio}' para el usuario {sys_usr(usuario_sistema_id)}")
            cur.execute(sql_search, (patron_busqueda, usuario_sistema_id))
            filas = cur.fetchall() #con fetchall se listan todas las filas encontradas y damos paso a la logica para que tenga que haber un nombre

            if filas: # Si se encontraron resultados
                logger.info(f"Se encontraron {len(filas)} resultados para '{nombre_buscado_limpio}'")
                return filas, nombre_buscado # Retorna las filas encontradas y el nombre y sale del bucle
            else: # Si no se encontraron resultados, se le da la opción al usuario de intentar de nuevo o salir
                logger.info(f"No se encontraron resultados para '{nombre_buscado_limpio}'")
                print(f"No se encontraron resultados para '{nombre_buscado}'. Intente de nuevo.")
                nombre_buscado = input("Ingrese el nombre a buscar: ")
            
            cur.close() # Cerrar el cursor después de cada ejecución
        except (Exception, psycopg.Error) as e:
            logger.error(f"ERROR al buscar el cliente '{nombre_buscado_limpio}': {e}")
            print(f"ERROR, no se puede conectar ni consultar con la DB\nDetalles: {e}")
            break # Salir del bucle en caso de error de DB
        finally:
            if conn:
                conn.close()
            if cur:
                cur.close()

#  LISTAR LOS MOVIMIENTOS
def historial_movimientos(cliente_id, usuario_sistema_id, limite=10):
    """
    Obtiene el historial de movimientos de la tabla movimientos, de un cliente especifico, basandose en el id del cliente y el user id, el limite es para establecer cuantos movimientos se quieren consultar
    
    devuelve la lista de movimientos o una lista vacia si no hay movimientos
    """
    conn = db_conection()
    if conn is None:
        return False
    
    cur = None
    try:
        cur = conn.cursor()
        #sentencia para seleccionar movimientos, ordenarlos por fecha y id de forma descendente y opcionalmente limitarlos
        sql_movimientos = """
        SELECT
            mv.id,
            mv.fecha_movimiento,
            mv.tipo_movimiento,
            mv.monto,
            mv.saldo_anterior,
            mv.saldo_final,
            c.nombre AS nombre_cliente
        FROM
            movimientos mv
        INNER JOIN
            clientes c ON mv.cliente_id = c.id
        WHERE
            mv.cliente_id = %s AND mv.usuario_sistema_id = %s
        ORDER BY
            mv.fecha_movimiento DESC, mv.id DESC
        LIMIT %s;
        """
        # parametros = [cliente_id, usuario_sistema_id]
        
        # if limite is not None and isinstance(limite, int) and limite > 0: #si limite no es None, y es un numero entero, y es mayor a cero
        #     sql_movimientos += "LIMIT %s" #agregamos a la sentencia, el limite con su placeholder
        #     parametros.append(limite) #añadimos limite a los parametros
        logger.info(f"Intentando obtener historial de movimientos para el cliente ID: {cliente_id}")
        cur.execute(sql_movimientos, (cliente_id, usuario_sistema_id, limite))
        movimientos = cur.fetchall() #asignamos a la variable movimientos lo que hemos obtenido de la consulta
        
        if movimientos: #si no esta vacio
            logger.info(f"Se encontraron {len(movimientos)} movimientos para el cliente ID: {cliente_id}")
            return movimientos #retorna los valores obtenidos de la consulta
        else:
            logger.info(f"No se encontraron movimientos para el cliente ID: {cliente_id}")
            print(f"No se encontraron movimientos para el cliente ID: {cliente_id}")
            return [] #devolvemos una lista vacia
    
    except psycopg.Error as e: #capturamos errores generales
        logger.error(f"ERROR al obtener historial de movimientos para {cliente_id}: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            logger.info("/// CONEXION A LA BASE DE DATOS CERRADA ///")

#  REGISTRAMOS EL MOVIMIENTO EN LA DB
def registrar_movimiento(cliente_id, tipo_movimiento, monto, saldo_anterior, saldo_final, usuario_sistema_id):
    """
    REGISTRA UN MOVIMIENTO EN LA TABLA MOVIMIENTOS
    
    Args:
        cliente_id (int) ID del cliente que tuvo el movimiento
        tipo_movimiento (str) Tipo de movimiento ('deuda_inicial', 'abono', 'actualizacion')
        monto (Decimal) Monto del movimiento
        saldo_anterior (Decimal) Saldo anterior del cliente
        saldo_final (Decimal) Saldo final del cliente
        usuario_sistema_id (int) ID del usuario que realizo el movimiento
    Returns:
        bool: True si se registro con exito, False en caso contrario
    """
    conn = db_conection()
    if conn is None:
        return False
    
    cur = None
    try:
        cur = conn.cursor()
        
        #sentencia SQL para insertar el movimiento
        insertar_movimiento_sql = """
        INSERT INTO movimientos (
            cliente_id,
            tipo_movimiento,
            monto,
            saldo_anterior,
            saldo_final,
            usuario_sistema_id
        ) VALUES (
            %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        
        #ejecutamos la insercion
        cur.execute(insertar_movimiento_sql, (
            cliente_id,
            tipo_movimiento,
            monto,
            saldo_anterior,
            saldo_final,
            usuario_sistema_id
        ))
        
        movimiento_id = cur.fetchone()[0] #type: ignore
        #obtenemos el id del movimiento 
        conn.commit()
        
        logger.info(f"Movimiento registrado con ID: {movimiento_id}")
        return True
    except psycopg.Error as e:
        logger.error(f"ERROR al registrar movimiento: {e}")
        if conn: conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            logger.info("/// CONEXION A LA BASE DE DATOS CERRADA ///")

# OBTENEMOS EL ULTIMO MOVIMIENTO DE UN CLIENTE
def ultimo_movimiento(cliente_id, usuario_sistema_id, limite=3):
    ultimomovimiento = historial_movimientos(cliente_id, usuario_sistema_id, limite)
    if ultimomovimiento:
        for fila in ultimomovimiento:
            fecha = fila[1].strftime("%d/%m/%y")
            tipo = fila[2].replace('_', ' ')
            monto = fila[3]
            saldo_anterior = fila[4]
            saldo_final = fila[5]
            print(f"| {fecha} Tipo: --{tipo.upper()}-- Saldo Anterior: {saldo_anterior} Monto: {monto} Saldo Final: {saldo_final}")
            print('=' * 80)
    else:
        print(f"\n No se encontraron movimientos para el cliente ID {cliente_id}")

