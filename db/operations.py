# conectar la base de datos
import psycopg #importamos la libreria para 'hablar' con la DB
from datetime import date #esto es para la fecha de adquisicion
from psycopg.errors import UniqueViolation, ForeignKeyViolation # importamos el error especifico
from decimal import Decimal #importamos decimal para uso con saldos
import logging


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
#####----------------------//////FUNCIONES/////-------------------######

#creamos una funcion para establecer y devolver una conexion nueva a la DB
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

#funcion para definir el nombre del usuario del sistema actual
def sys_usr(usuario_sistema_id):
    user = None
    if usuario_sistema_id == 1:
        user = "ZURIEL"
    elif usuario_sistema_id == 2:
        user = "SERGIO"
    return user

#--CREAMOS UNA FUNCION PARA CREAR LA BASE DE DATOS--
def crear_tabla_clientes():
    """
    CONECTAMOS LA BASE DE DATOS Y CREAMOS LA TABLA CLIENTES
    """
    conn = db_conection()
    if conn is None: #definimos que si hubo un error al tratar de conectar nos devuelva
        return False #No se pudo establecer la conexion
    
    cur = None #esta la variable cursor, asi nos aseguramos que siempre existan

    try:
        cur = conn.cursor() 
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS clientes(
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            telefono VARCHAR(50),
            ubicacion_aproximada TEXT,
            foto_domicilio VARCHAR(255),
            comentario TEXT,
            fecha_adquisicion DATE,
            saldo_actual NUMERIC(10, 2) DEFAULT 0.00,
            estado_cliente VARCHAR(50) DEFAULT 'regular',
            usuario_sistema_id INTEGER NOT NULL,
            CONSTRAINT uq_nombre_id_usuario UNIQUE (nombre, usuario_sistema_id)
        );
        """ #esta es la 'sentencia' le decimos que columnas queremos crear y con que parametros
            #añadimos la restriccion al final de la sentencia
        logger.info("INTENTANDO CREAR TABLA 'CLIENTES'...")
        cur.execute(create_table_sql) #le indicamos al 'cursor' que ejecute la sentencia create_table_sql
        conn.commit() #hacemos 'commit' o guardamos los cambios de forma permanente
        logger.info("TABLA 'CLIENTES' CREADA O YA EXISTENTE...")
        return True #indicamos que fue exitoso

    except psycopg.Error as e:
        logger.error(f"/// ERROR AL CONECTAR O CREAR TABLA: {e} ///")
        if conn:
            conn.rollback()
        return False
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            logger.info("/// CONEXION A LA BASE DE DATOS CERRADA ///")

#---------////////  funcion para agregar clientes a la DB   /////////--------
def agregar_cliente(nombre, telefono, ubicacion, foto_domicilio, comentario, usuario_sistema_id
    ):
    """
    Agrega un nuevo cliente a la DB, sin duplicados por id
    """
    conn = db_conection() #conectamos a al DB
    if conn is None: #si hay problemas
        return False #devolvemos false
    
    cur = None
    try:
        user = sys_usr(usuario_sistema_id)
        cur = conn.cursor()
        # 'sentencia' para hacer el insert
        insert_sql = """
        INSERT INTO clientes (nombre,
        telefono,
        ubicacion_aproximada,
        foto_domicilio,
        comentario,
        fecha_adquisicion,
        usuario_sistema_id)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
        RETURNING id; -- OBTENEMOS EL id DEL CLIENTE INSERTADO
        """
        # con date.today() añadimos la fecha de adquisicion por defecto
        cur.execute(insert_sql, (nombre, telefono, ubicacion, foto_domicilio, comentario, date.today(), usuario_sistema_id)) #aqui le pedimos al cursor que ejecute la sentencia sql, con los valores que le indicamos
        cliente_id = cur.fetchone()[0] # type: ignore
        conn.commit()
        logger.info(f'Cliente "{nombre}" ah sido agregado con exito, id: {cliente_id}')
        print(f'Cliente "{nombre}" ah sido agregado con exito, id: {cliente_id}')
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

#------///// funcion para obtener todos los clientes para un usuario especifico /////////------
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

        #obtenemos los nombres de las columnas para mejor legibilidad
        column_names = [desc[0] for desc in cur.description] # type: ignore
        logger.info(f"\nObteniendo clientes del usuario {user}\n")
        #los prints para la cli se mantienen
        print(f"\nObteniendo clientes del usuario {user}\n")
        print("|".join(column_names))
        print("-" * (len("|".join(column_names))))

        for row in cur.fetchall():
            #Formateamos la fila
            formated_row = [str(col) if col is not None else "N/A" for col in row]
            print("|".join(formated_row)) #imprimimos como fila formateada
            clientes.append(row) # Tambien podemos guardar las tuplas en una lista
        
        return clientes

    except psycopg.Error as e:
        logger.error(f'Error al obtener clientes: {e}')
        return [] # regresamos a la lista vacia
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        #cerramos cursor y conexion

#####------------------////// FUNCION PARA ACTUALIZAR UNA FILA/////----------------------
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

#####------------------////// FUNCION PARA ACTUALIZAR SALDOS/////----------------------
def actualizar_saldo(cliente_id, usuario_sistema_id, nuevo_saldo):
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
        user = sys_usr(usuario_sistema_id)
    
        cur = conn.cursor()
        #sentencia SQL para sumar/restar al saldo actual
        update_saldo_sql = """
        UPDATE clientes
        SET saldo_actual = saldo_actual + %s
        WHERE id = %s AND usuario_sistema_id = %s;
        """
        
        #ejecutamos la sentencia, debemos pasar los valores tal como definimos la sentencia psycopg convierte automaticamente Decimal a NUMERIC
        cur.execute(update_saldo_sql, (nuevo_saldo, cliente_id, usuario_sistema_id))
        #usamos rowcount para verificar si realmente se hizo algun movimiento
        if cur.rowcount > 0:
            conn.commit() #guardamos cambios
            logger.info(f"Saldo cliente ID {cliente_id} (usuario {user}) actualizado) con {nuevo_saldo}")
            print(f"\nSaldo del cliente actualizado")
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

#----------------///////// FUNCION PARA LISTAR UN SOLO CLIENTE ///////----------------------
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
                logger.debug(f"Cliente ID {cliente_id} listado con exito")
                print(f"\n//--ID: {encontrado[0]}, Nombre: {encontrado[1]}, Telefono: {encontrado[2]}, Saldo: ${encontrado[7]}--//")
                return encontrado # RETORNA EL CLIENTE ENCONTRADO Y SALE DEL BUCLE
            else:
                logger.info(f"\nNo se encontraron datos para el ID {cliente_id} (usuario {user})")
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

#----------------///////// FUNCION PARA ELIMINAR CLIENTES ///////----------------------
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
            print(f"Cliente con ID: {cliente_id} (Usuario: {user}) eliminado")
            return True
        else:
            conn.rollback() #si el rowcount es 0, el cliente no se encontro o no existe y deshacemos
            logger.warning(f"Cliente con ID {cliente_id} (Usuario {user}) no encontrado")
            print(f"---ERROR---\nCliente con ID {cliente_id} (Usuario {user}) no encontrado")
            return False
    except ForeignKeyViolation as e:
        #capturamos el error si el cliente esta en otra tabla
        logger.error(f"ERROR de clave foranea al eliminar cliente con ID {cliente_id}.\nDetalle\n{e}")
        print(f"No se pudo eliminar cliente con ID {cliente_id}, debido a deoendencia en otra tabla.\nDetalle\n{e}")
        if conn:
            conn.rollback()
            return False
    except psycopg.Error as e:
        logger.error(f"ERROR general el eliminar cliente ID {cliente_id}.\n(GENERAL - ERROR)\n{e}")
        print(f"ERROR al eliminar cliente con ID {cliente_id}.\n(GENERAL - ERROR)\n{e}")
        if conn:
            conn.rollback()
            return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

#----------------///////// FUNCION PARA BUSQUEDA DE CLIENTES ///////----------------------
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
                SELECT id, --0
                nombre, --1
                telefono, --2
                ubicacion_aproximada, --3
                foto_domicilio, --4
                comentario, --5
                fecha_adquisicion, --6
                saldo_actual, --7
                estado_cliente, --8
                usuario_sistema_id --9
                FROM clientes
                WHERE TRIM(nombre) ILIKE TRIM(%s) AND usuario_sistema_id = (%s);
                """
            patron_busqueda = f"{nombre_buscado.strip()}%"
            logger.info(f"Buscando clientes con nombre '{nombre_buscado_limpio}' para el usuario {sys_usr(usuario_sistema_id)}")
            cur.execute(sql_search, (patron_busqueda, usuario_sistema_id))
            filas = cur.fetchall() #con fetchall se listan todas las filas encontradas y damos paso a la logica para que tenga que haber un nombre

            if filas: # Si se encontraron resultados
                logger.info(f"Se encontraron {len(filas)} resultados para '{nombre_buscado_limpio}'")
                print(f"\nResultados para '{nombre_buscado}' \n")
                for fila in filas:
                    print(f"ID: {fila[0]}, Nombre: {fila[1]}, Telefono: {fila[2]}, Ubicacion: {fila[3]}, Comentario: {fila[5]}, Saldo: ${fila[7]}.")
                break # Salir del bucle si se encontraron resultados
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
