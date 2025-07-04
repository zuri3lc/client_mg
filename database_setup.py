# conectar la base de datos
import psycopg

#-------configuracion de la conexion a PostgreSQL----------
# --Datos de la BD--
DB_NAME = "clients_db"
DB_USER = "gestor_clientes"
DB_PASSWORD = "RettkeStysi@k208"
DB_HOST = "192.168.1.113"
DB_PORT = "5433"

#-- CADENA DE CONEXION --
conn_string = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

#--CREAMOS UNA FUNCION PARA CREAR LA BASE DE DATOS--
def crear_tabla_clientes():
    """
    CONECTAMOS LA BASE DE DATOS Y CREAMOS LA TABLA CLIENTES
    """
    conn = None #esta inicializa la variable conn para la conexion
    cur = None #esta la variable cursor, asi nos aseguramos que siempre existan
    try:
        #codigo de conexion a la DB
        print(f"INTENTANDO CONECTAR A LA DB '{DB_NAME}' EN {DB_HOST}:{DB_PORT}...")
        conn = psycopg.connect(conn_string)
        print(f"CONEXION EXITOSA A {DB_NAME} PostgreSQL")

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
        """
        print("CREANDO TABLA 'CLIENTES'...")
        cur.execute(create_table_sql)
        conn.commit()
        print("TABLA 'CLIENTES' CREADA O YA EXISTENTE...")

    except psycopg.Error as e:
        print(f"/// ERROR AL CONECTAR O CREAR TABLA: {e} ///")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            print("/// CONEXION A LA BASE DE DATOS CERRADA ///")
if __name__ == "__main__":
    crear_tabla_clientes()