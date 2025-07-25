# conectar la base de datos
#from asyncio.exceptions import LimitOverrunError
import os
from dotenv import load_dotenv
load_dotenv()
import psycopg #importamos la libreria para 'hablar' con la DB
from psycopg.rows import dict_row
from datetime import date #esto es para la fecha de adquisicion
from psycopg.errors import UniqueViolation, ForeignKeyViolation # importamos el error especifico
from decimal import Decimal #importamos decimal para uso con saldos
import logging
import bcrypt


#-------configuracion de la conexion a PostgreSQL----------
# --ENV con Datos de la BD--
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

#------------- BLOQUE DE CONEXION A LA DB --------------------------
#-- CADENA DE CONEXION (esta linea conecta a la base de datos) --
conn_string = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

#--------------- CONFIGURACION LOGGER ------------------
logging.basicConfig(
    level=logging.INFO, #definimos la severidad del log
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', #define el formato del log
    handlers=[
        logging.FileHandler("app_log.log"), #guarda los logs en el archivo app_log.log
        #logging.StreamHandler() #imprime los logs en la consola
    ]
)
logger = logging.getLogger(__name__) #creamos un logger para este modulo

#===================== FUNCIONES (CONEXION Y TBLAS) =====================

#  ESTABLECE UNA CONEXION A LA DB
def db_conection():
    """ESTABLECE Y DEVUELVE UNA NUEVA CONEXIÓN A LA DB"""
    try:
        conn = psycopg.connect(conn_string) #nos conectamos a la DB
        logger.info("Conexion a la DB establecida con exito")
        return conn
    except psycopg.Error as e: # 'atrapamos' los errores y los guardamos en una variable llamada e
        logger.critical(f"ERROR AL CONECTAR A LA DB: {e}")
        return None #terminamos la conexión nueva

# -------- CREACION DE TABLAS ---------
def crear_tablas():
    """CONECTAMOS LA BASE DE DATOS Y CREAMOS LA TABLA CLIENTES Y MOVIMIENTOS
    Retorna True si todo sale bien, False si hay algun error"""
    conn = db_conection()
    if conn is None: return False #No se pudo establecer la conexion
    try:
        with conn.cursor() as cur:
            # ---------------- TABLA USUARIOS DEL SISTEMA ----------------
            cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios(
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL, -- restriccion de unicidad
                password_hash VARCHAR(255) NOT NULL,
                nombre VARCHAR(255),
                fecha_creacion DATE NOT NULL DEFAULT CURRENT_DATE
            );
            """
            )
            # ---------------- TABLA CLIENTES ----------------
            cur.execute ("""
            CREATE TABLE IF NOT EXISTS clientes(
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                telefono VARCHAR(50),
                ubicacion_aproximada TEXT,
                foto_domicilio VARCHAR(255),
                comentario TEXT,
                fecha_adquisicion DATE NOT NULL DEFAULT CURRENT_DATE,
                fecha_ultima_modificacion DATE NOT NULL DEFAULT CURRENT_DATE,
                last_updated TIMESTAMPTZ DEFAULT NOW(),
                saldo_actual NUMERIC(10, 2) DEFAULT 0.00,
                estado_cliente VARCHAR(50) DEFAULT 'regular',
                usuario_sistema_id INTEGER NOT NULL,
                CONSTRAINT uq_nombre_id_usuario UNIQUE (nombre, usuario_sistema_id),
                CONSTRAINT fk_usuario_sistema FOREIGN KEY (usuario_sistema_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
            """
            )
            # uq_nombre_id_usuario restriccion de unicidad para evitar duplicados el nombre del cliente y el id del usuario del sistema
            #fk_usuario_sistema relaciona la tabla clientes con la tabla usuarios del sistema
            # ----------------- TABLA MOVIMIENTOS -----------------
            cur.execute("""
            CREATE TABLE IF NOT EXISTS movimientos(
                id SERIAL PRIMARY KEY,
                cliente_id INTEGER NOT NULL,
                fecha_movimiento DATE NOT NULL DEFAULT CURRENT_DATE,
                tipo_movimiento VARCHAR(50) NOT NULL CHECK (tipo_movimiento IN ('deuda_inicial', 'abono', 'cargo')),
                monto NUMERIC(10, 2) NOT NULL,
                saldo_anterior NUMERIC(10, 2) NOT NULL,
                saldo_final NUMERIC(10, 2) NOT NULL,
                last_updated TIMESTAMPTZ DEFAULT NOW(),
                usuario_sistema_id INTEGER NOT NULL,
                CONSTRAINT fk_cliente_movimiento FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
            );
            """ # fk_cliente_movimiento relaciona la tabla movimientos con la tabla clientes
            )
        
            logger.info("INTENTANDO CREAR TABLA 'USUARIOS'...")
            logger.info("INTENTANDO CREAR TABLA 'CLIENTES'...")
            logger.info("INTENTANDO CREAR TABLA 'MOVIMIENTOS'...")
            
            conn.commit() #hacemos 'commit' o guardamos los cambios de forma permanente
            logger.info("TABLAS CREADAS EXITOSAMENTE O YA EXISTENTE...")
        return True #indicamos que fue exitoso
    except psycopg.Error as e:
        logger.error(f"/// ERROR AL CONECTAR O CREAR LAS TABLAS: {e} ///")
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()
        logger.info("/// CONEXION A LA BASE DE DATOS CERRADA ///")

#========================= FUNCIONES PARA USUARIOS ====================

# REGISTRAR UN NUEVO USUARIO
def registrar_usuario_db(username, password, nombre=None):
    """Registra un nuevo usuario en la base de datos."""
    # 1. Hashear la contraseña password.encode('utf-8') convierte la contraseña de string a bytes
    #2 - bcrypt.gensalt() genera una sal aleatorio para hacer el hash mas seguro
    #3 - bcrypt.hashpw() aplica el hash a la contraseña y la sal, creando un hash seguro
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = db_conection() #conectamos a la DB
    if conn is None: return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO usuarios (
                username,
                password_hash,
                nombre)
            VALUES (
                %s, %s, %s)
            RETURNING id;
                """,
            (username, password_hash.decode('utf-8'), nombre) #valores para la sentencia
            )
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
        if conn: conn.close()

# VERIFICA LAS CREDENCIALES DEL USUARIO
def verificar_credenciales_db(username, password):
    """Verifica las credenciales del usuario en la base de datos. Devuelve el ID del usuario si las credenciales son correctas, de lo contrario, devuelve None."""
    conn = db_conection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT id, password_hash FROM usuarios WHERE username = %s;
            """,
            (username,) #tupla con un solo elemento
            )
            user_data = cur.fetchone() #obtenemos una fila de la consulta
            if user_data: #si hay datos
                user_id, password_hash = user_data
                #verificamos si la contraseña coincide con el hash almacenado
                # bcrypt.checkpw() compara la contraseña ingresada con el hash almacenado
                if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    #checkpw => convertimos la contraseña a bytes y el hash a bytes y comparamos
                    logger.info(f"Credenciales correctas {username}")
                    return user_id # PASS devolvemos el user_id
                logger.warning(f"Contraseña incorrecta para el usuario '{username}'")
                return None # None si la contraseña es incorrecta
            else:
                logger.warning(f"Usuario '{username}' no encontrado")
                return None # Usuario no encontrado
    except psycopg.Error as e:
        logger.error(f"Error al verificar las credenciales\nDetalles: {e}")
        return None
    finally:
        if conn: conn.close()

#  DEFINE EL NOMBRE DEL USUARIO DE LA SESION ACTUAL
def get_username_by_id_db(usuario_sistema_id):
    """"
    DEVUELVE EL NOMBRE DEL USUARIO DEL SISTEMA
    """
    conn = db_conection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT username FROM usuarios WHERE id = %s;
            """,
            (usuario_sistema_id,) #tupla con un solo elemento
            )
            resultado = cur.fetchone() #Type: ignore
            if resultado:
                return resultado[0].upper() if resultado else "Desconocido" #type: ignore
    except psycopg.Error as e:
        logger.error(f"Error al obtener el nombre del usuario: {e}")
        return "Desconocido" # nombre por defecto si hay un error
    finally:
        if conn: conn.close()

# VERIFICA SI EL NOMBRE DE USUARIO YA EXISTE
def check_username_exist_db(username):
    """Verifica si el nombre de usuario ya existe en la base de datos."""
    conn = db_conection()
    if conn is None: return True #Asumimos que existe para evitar un duplicado que fallará
    try:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT 1 FROM usuarios WHERE username = %s;
            """, # solo le estamos diciendo a la db que si encuentra un duplicado devuelva 1, la consulta se detiene inmediatamente
            (username,)) #tupla con un solo elemento
            return cur.fetchone() is not None #evalua si la consutla devolvio una tupla, sin importar el valor (el usuario existe), si devuelve None (el usuario no existe)
    except psycopg.Error as e:
        logger.error(f"Error al verificar el nombre de usuario {username}: {e}")
        return True
    finally:
        if conn: conn.close()

#==================== FUNCIONES PARA CLIENTES ===================

#  VERIFICAMOS SI EL NOMBRE EXISTE EN LA DB
def check_client_name_exist_db(nombre, usuario_sistema_id, exclude_client_id=None):
    """verifica si el nombre del cliente ya existe en la DB ligado al usuario actual"""
    conn = db_conection()
    if conn is None: return True
    try:
        with conn.cursor() as cur:
            query = """
            SELECT 1 FROM clientes
            WHERE TRIM(nombre) ILIKE TRIM(%s) AND usuario_sistema_id = (%s);
            """
            params = [nombre, usuario_sistema_id]
            if exclude_client_id is not None:
                query += " AND id != (%s);" #condicion para añadir el ID
                params.append(exclude_client_id) #añadimos a la lista
            cur.execute(query, tuple(params)) #pasamos a ejecutar convirtiendo a tupla
            
            return cur.fetchone() is not None            
    except psycopg.Error as e:
        logger.error(f"Error al verificar el nombre del cliente {nombre}: {e}")
        return True #FailSafe, para evitar duplicados
    finally:
        if conn: conn.close()

#  AGREGAR CLIENTES
def agregar_cliente_db(nombre, telefono, ubicacion, foto_domicilio, comentario, saldo_inicial, usuario_sistema_id
    ): 
    """Agrega un nuevo cliente a la DB, sin duplicados por id"""
    conn = db_conection() #conectamos a al DB
    if conn is None: return None
    try:
        with conn.cursor() as cur:
            # paso 1 insertar el cliente
            cur.execute("""
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
            """,
            (nombre,
            telefono,
            ubicacion,
            foto_domicilio,
            comentario,
            date.today(),
            saldo_inicial,
            usuario_sistema_id
            ))
            cliente_id = cur.fetchone()[0] # type: ignore
            #paso 2 insertamos el saldo inicial del cliente
            cur.execute("""
            INSERT INTO movimientos (
                cliente_id,
                tipo_movimiento,
                monto,
                saldo_anterior,
                saldo_final,
                usuario_sistema_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s)
            """,
            (
            cliente_id,
            'deuda_inicial',
            saldo_inicial, #en este contexto exclusivamente saldo_inicial es lo mismo que saldo final
            0.00,
            saldo_inicial,
            usuario_sistema_id
                ))
            conn.commit()
            logger.info(f'Cliente "{nombre}" ah sido agregado con exito, id: {cliente_id}')
            return cliente_id # devuelve el id del nuevo cliente
    #----////CON ESTE BLOQUE CAPTURAMOS EL ERROR DE Unique.Violaton/////-----
    except UniqueViolation as e: # capturamos el error especifico de unicidad
        logger.warning(f"ERROR: El cliente '{nombre}' ya existe para tu usuario.\nDetalle: \n {e}") # type: ignore
        return None
    #----////AQUI CERRAMOS EL BLOQUE DE CAPTURA DEL ERROR Unique.Violaton/////-----
    except psycopg.Error as e: #manejo de errores si psycopg tiene algun error
        logger.error(f"Error al agregar cliente {nombre}: {e}")
        return None
    finally:
        if conn: conn.close()

#  OBTENEMOS TODOS LOS CLIENTES DE UN USUARIO
def obtain_clients_db(usuario_sistema_id):
    """OBTIENE TODOS LOS CLIENTES DE UN USUARIO ESPECIFICO"""
    conn = db_conection()
    if conn is None: return [] #Devuelve una lista vacia si hay algun problema con la conexion
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            # seleccionamos todas las columnas (*) y filtramos por usuario del sistema
            cur.execute("""
                        SELECT
                            id,
                            nombre,
                            telefono,
                            ubicacion_aproximada,
                            foto_domicilio,
                            comentario,
                            fecha_adquisicion,
                            fecha_ultima_modificacion,
                            saldo_actual,
                            estado_cliente,
                            usuario_sistema_id
                        FROM
                            clientes 
                        WHERE
                            usuario_sistema_id = %s ORDER BY ID;""",
                        (usuario_sistema_id,))
            return cur.fetchall()
    except psycopg.Error as e:
        logger.error(f'Error al obtener clientes: {e}')
        return [] # regresamos a la lista vacia
    finally:
        if conn: conn.close()

#  LISTAR UN SOLO CLIENTE
def list_client_db(cliente_id, usuario_sistema_id):
    conn = db_conection()
    if conn is None: return None
    try:
        user = get_username_by_id_db(usuario_sistema_id)
        with conn.cursor(row_factory=dict_row) as cur:
            #seleccionamos la columna y la fila
            cur.execute("""
                        SELECT
                            id,
                            nombre,
                            telefono,
                            ubicacion_aproximada,
                            foto_domicilio,
                            comentario,
                            fecha_adquisicion,
                            fecha_ultima_modificacion,
                            saldo_actual,
                            estado_cliente,
                            usuario_sistema_id
                        FROM
                            clientes 
                        WHERE
                            id = %s AND usuario_sistema_id = %s;""",
                        (cliente_id, usuario_sistema_id))
            
            logger.info(f"\nCliente ID {cliente_id} listado con exito")
            return cur.fetchone()
    except (Exception, psycopg.Error) as e:
        logger.error(f"ERROR al listar el cliente con ID {cliente_id} (general ERROR): {e}")
        print(f"ERROR, no se puede conectar ni consultar con la DB\n")
        return None # Sale del bucle en caso de error de DB
    finally:
        if conn: conn.close()

#  ACTUALIZAR UNA FILA/CLIENTE
def client_update_db(cliente_id, usuario_sistema_id, **kwargs):
    # 1ro verificamos si se pasaron campos para actualizar
    if not kwargs: return False
    conn = db_conection()
    if conn is None: return False
    set_clauses = [f"{key} = %s" for key in kwargs.keys()]
    values = list(kwargs.values())
    values.extend([cliente_id, usuario_sistema_id])
    
    update_sql = f"UPDATE clientes SET {','.join(set_clauses)}, last_updated = CURRENT_TIMESTAMP, fecha_ultima_modificacion = CURRENT_DATE WHERE id = %s AND usuario_sistema_id = %s;"

    try:
        with conn.cursor() as cur:
            cur.execute(update_sql, tuple(values)) #type: ignore
            if cur.rowcount > 0:
                conn.commit() #guardamos
                logger.info(f"Cliente con id {cliente_id}")
                return True
            return False
    except UniqueViolation as e:
        logger.warning(f"--ERROR--\nNo se pudo actualizar cliente con ID {cliente_id}, la combinacion Nombre/Usuario ya existe")
        return False
    except psycopg.Error as e:
        logger.error(f"--ERROR--\nNo se pudo actualizar el cliente con ID {cliente_id} (general ERROR): {e}")
        return False
    finally:
        if conn: conn.close()

#  ACTUALIZAR SALDOS
def actualizar_saldo_db(cliente_id, usuario_sistema_id, monto):
    """ACTUALIZA EL SALDO DE UN CLIENTE ESPECIFICO, FILTRADO POR SU ID Y EL ID DEL PROPIETARIO DEL CLIENTE"""
    conn = db_conection()
    if conn is None: return False
    try:
        with conn.cursor() as cur:
            # 1: obtener el saldo actual del cliente
            cur.execute("""
            SELECT saldo_actual FROM clientes WHERE id = %s AND usuario_sistema_id = %s;
            """,
            (cliente_id,
            usuario_sistema_id)
            )
            resultado = cur.fetchone()
            if not resultado:
                logger.warning(f"Cliente con ID {cliente_id} no encontrado")
                return False
            
            saldo_anterior = resultado[0] #type: ignore
            saldo_final = saldo_anterior + monto
            
            # Paso 2: Actualizar saldo del cliente
            cur.execute("""
            UPDATE clientes
            SET 
                saldo_actual = %s,
                fecha_ultima_modificacion = CURRENT_DATE,
                last_updated = CURRENT_TIMESTAMP
            WHERE id = %s AND usuario_sistema_id = %s;
            """,
            (saldo_final, #actualizamos la fecha de ultima modificacion
            cliente_id,
            usuario_sistema_id)
            )
            
            # Paso 3: Determinar el tipo de movimiento
            tipo_movimiento = 'cargo' if monto > 0 else 'abono'
            registrar_movimiento_interno(cur, cliente_id, tipo_movimiento, monto, saldo_anterior, saldo_final, usuario_sistema_id)
            conn.commit() #guardamos los cambios
            logger.info(f"Saldo del cliente ID {cliente_id} actualizado a {saldo_final}")
            return True
    except psycopg.Error as e:
        logger.error(f"ERROR al actualizar saldo: {e}")
        return False
    finally:
        if conn: conn.close()

#  ELIMINAR CLIENTES
def eliminar_cliente_db(cliente_id, usuario_sistema_id):
    """ELIMINA UN CLIENTE ESPECIFICO BASANDOSE EN SU ID Y EL ID USUARIO PROPIETARIO"""
    conn = db_conection()
    if conn is None: return False
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM clientes WHERE id = %s AND usuario_sistema_id = %s;", 
            (cliente_id, usuario_sistema_id))
            if cur.rowcount > 0:
                conn.commit() #solo guardamos si rowcount nos confirma que se elemino alguna fila
                logger.info(f"Cliente con ID: {cliente_id} eliminado con exito")
                return True
            return False
    except ForeignKeyViolation as e:
        logger.error(f"ERROR al eliminar cliente con ID {cliente_id}.\nDetalle\n{e}")
        return False
    except psycopg.Error as e:
        logger.error(f"ERROR el eliminar cliente ID {cliente_id}.\n(GENERAL - ERROR)\n{e}")
        return False
    finally:
        if conn: conn.close()

#  BUSQUEDA DE CLIENTES
def client_search_db(nombre_buscado, usuario_sistema_id):
    conn = db_conection()
    if conn is None: return []
    try:
        with conn.cursor() as cur:
            patron_busqueda = f"%{nombre_buscado.strip()}%"
            cur.execute("""
                SELECT
                    id,
                    nombre,
                    telefono,
                    ubicacion_aproximada,
                    foto_domicilio,
                    comentario,
                    fecha_adquisicion,
                    fecha_ultima_modificacion,
                    saldo_actual,
                    estado_cliente
                FROM
                    clientes
                WHERE nombre ILIKE %s AND usuario_sistema_id = %s;""",
                (patron_busqueda, usuario_sistema_id))
            return cur.fetchall()
    except (Exception, psycopg.Error) as e:
        logger.error(f"ERROR al buscar el cliente '{nombre_buscado}': {e}")
        return []
    finally:
        if conn: conn.close()

#  LISTAR LOS MOVIMIENTOS
def historial_movimientos_db(cliente_id, usuario_sistema_id, limite=10):
    conn = db_conection()
    if conn is None: return []
    try:
        with conn.cursor() as cur:
            cur.execute("""
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
            ORDER BY mv.fecha_movimiento DESC, mv.id DESC LIMIT %s;""",
            (cliente_id, usuario_sistema_id, limite)
            )
            return cur.fetchall()
    except psycopg.Error as e: #capturamos errores generales
        logger.error(f"ERROR al obtener historial de movimientos para {cliente_id}: {e}")
        return None
    finally:
        if conn: conn.close()
        logger.info("/// CONEXION A LA BASE DE DATOS CERRADA ///")

# FUNCION PARA REGISTRAR UN MOVIMIENTO USANDO UN CURSOS EXISTENTE
def registrar_movimiento_interno(cursor, cliente_id, tipo, monto, saldo_anterior, saldo_final, user_id):
    cursor.execute(
        """INSERT INTO movimientos (cliente_id, tipo_movimiento, monto, saldo_anterior, saldo_final, usuario_sistema_id)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (cliente_id, tipo, monto, saldo_anterior, saldo_final, user_id)
    )

