# conectar la base de datos
import psycopg #importamos la libreria para 'hablar' con la DB
from datetime import date #esto es para la fecha de adquisicion

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

#creamos una funcion para establecer y devolver una conexion nueva a la DB
def db_conection():
    """
    ESTABLECE Y DEVUELVE UNA NUEVA CONEXIÓN A LA DB
    """
    try:
        conn = psycopg.connect(conn_string) #nos conectamos a la DB
        return conn
    except psycopg.Error as e: # 'atrapamos' los errores y los guardamos en una variable llamada e
        print(f"ERROR AL CONECTAR A LA DB: {e}")
        return None #terminamos la conexión nueva
    
#---------------/////////////////EMPIEZA DEFINICION DE FUNCIONES///////////------------------

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
            ubicacion_aproximada TEXT,
            telefono VARCHAR(50),
            foto_domicilio VARCHAR(255),
            comentario TEXT,
            fecha_adquisicion DATE,
            saldo_actual NUMERIC(10, 2) DEFAULT 0.00,
            estado_cliente VARCHAR(50) DEFAULT 'regular',
            usuario_sistema_id INTEGER NOT NULL
        );
        """ #esta es la 'sentencia' le decimos que columnas queremos crear y con que parametros

        print("CREANDO TABLA 'CLIENTES'...")
        cur.execute(create_table_sql) #le indicamos al 'cursor' que ejecute la sentencia create_table_sql
        conn.commit() #hacemos 'commit' o guardamos los cambios de forma permanente
        print("TABLA 'CLIENTES' CREADA O YA EXISTENTE...")
        return True #indicamos que fue exitoso

    except psycopg.Error as e:
        print(f"/// ERROR AL CONECTAR O CREAR TABLA: {e} ///")
        if conn:
            conn.rollback()
        return False
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            print("\n/// CONEXION A LA BASE DE DATOS CERRADA ///")

#####-------//////FUNCIONES/////--------######

#-----/////  funcion para agregar clientes a la DB   /////////-----
def agregar_cliente(nombre, ubicacion, telefono, foto_domicilio, comentario, usuario_sistema_id):
    """
    Agrega un nuevo cliente a la DB
    """
    conn = db_conection() #conectamos a al DB
    if conn is None: #si hay problemas
        return False #devolvemos false
    
    cur = None
    try:
        cur = conn.cursor()
        # 'sentencia' para hacer el insert
        insert_sql = """
        INSERT INTO clientes (nombre,
        ubicacion_aproximada,
        telefono,
        foto_domicilio,
        comentario,
        fecha_adquisicion,
        usuario_sistema_id)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
        RETURNING id; -- OBTENEMOS EL id DEL CLIENTE INSERTADO
        """
        # con date.today() añadimos la fecha de adquisicion por defecto
        cur.execute(insert_sql, (nombre, ubicacion, telefono, foto_domicilio, comentario, date.today(), usuario_sistema_id)) #aqui le pedimos al cursor que ejecute la sentencia sql, con los valores que le indicamos
        cliente_id = cur.fetchone()[0] # type: ignore
        conn.commit()
        print(f'Cliente "{nombre}" ah sido agregado con exito, id: {cliente_id}')
        return cliente_id # devuelve el id del nuevo cliente
    except psycopg.Error as e: #manejo de errores si psycopg tiene algun error
        print(f"Error al agregar cliente: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

#-----/////    funcion para obtener todos los clientes para un usuario especifico   /////////-----
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
        cur = conn.cursor()
        # seleccionamos todas las columnas (*) y filtramos por usuario del sistema
        select_sql = "SELECT * FROM clientes WHERE usuario_sistema_id = %s ORDER BY ID;" #creamos una variable con la sentencia de busqueda
        cur.execute(select_sql, (usuario_sistema_id,)) #la comma es necesaria si solo hay un elemento en la tupla

        #obtenemos los nombres de las columnas para mejor legibilidad
        column_names = [desc[0] for desc in cur.description] # type: ignore
        print(f"Clientes del usuario con el ID: {usuario_sistema_id}")
        print("|".join(column_names))
        print("-" * (len("|".join(column_names))))

        for row in cur.fetchall():
            #Formateamos la fila
            formated_row = [str(col) if col is not None else "N/A" for col in row]
            print("|".join(formated_row)) #imprimimos como fila formateada
            clientes.append(row) # Tambien podemos guardar las tuplas en una lista
        
        return clientes

    except psycopg.Error as e:
        print(f'Error al obtener clientes: {e}')
        return [] # regresamos a la lista vacia
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        #cerramos cursor y conexion

#####-------////// FIN FUNCIONES/////--------######

#####-------//////INICIO DE LA LOGICA DE PRUEBA/////--------######

if __name__ == "__main__":
    print('---EJECUTANDO CONFIG INICIAL Y PRUEBAS DE CRUD---')

    # 1. (PRIMER PASO) ---- ASEGURARSE QUE LA TABLA EXISTA ----
    if crear_tabla_clientes():
        #el id del usuario actual lo estableceremos como 1 fijo temporalmente
        ID_USUARIO_ACTUAL = 1
        ID_2_PRUEBA = 2

        # 2. (PASO 2) --AGREGAR CLIENTES DE PRUEBA--
        print('\nAGREGANDO CLIENTES DE PRUEBA... \n')
        agregar_cliente("Juan Perez", "C 12 #32", "5544332233", "foto_juan.png", "Cliente Nuevo", ID_USUARIO_ACTUAL)
        agregar_cliente("Maria Garcia", "C 123 #252", "1122334455", "foto_maria.png", "Al Corriente", ID_USUARIO_ACTUAL)
        agregar_cliente("Carlos Lopez", "C Juana #1534", "9900220011", "foto_carlos.png", "Cuenta Atrasada", ID_USUARIO_ACTUAL)
        agregar_cliente("Zuriel Canche", "C 118a #921", "9992506511", "foto_z.png", "Al Corriente", ID_USUARIO_ACTUAL)

        # ----//// CLIENTES PARA EL USUARIO 2 ////----
        agregar_cliente("Ciente Prueba 2", "C Mala #21", "9923452367", "foto_2.png", "Cuenta Atrasada", ID_2_PRUEBA)
        agregar_cliente("Ciente Prueba 3", "C Pronto #56", "3456351468", "foto_3.png", "Cuenta Atrasada", ID_2_PRUEBA)
        agregar_cliente("Ciente Prueba 4", "C Soponcio #345", "2058838291", "foto_4.png", "Al Corriente", ID_2_PRUEBA)
        agregar_cliente("Ciente Prueba 5", "C Mala #55", "9923743567", "foto_5.png", "Cliente Nuevo", ID_2_PRUEBA)

        # 3. (PASO 3) --OBTENER Y MOSTRAR LOS CLIENTES DEL USUARIO ACTUAL
        print(f'\nOBTENIENDO CLIENTES DEL USUARIO {ID_USUARIO_ACTUAL}')
        user_clients = obtain_clients(ID_USUARIO_ACTUAL) 

        if user_clients:
            print(f'Total de clientes para el usuario {ID_USUARIO_ACTUAL}: {len(user_clients)}')
        else:
            print(f'No se encontraron clientes para el usuario {ID_USUARIO_ACTUAL}')
    else:
        print('NO SE PUDO INICIALIZAR LA DB, NO SE REALIZARON OPERACIONES --CRUD--')

