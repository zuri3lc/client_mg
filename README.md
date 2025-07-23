# Gestor de clientes

# Gestor de Clientes CLI

Este es un sistema de línea de comandos (CLI) para gestionar clientes, sus saldos y deudas, diseñado para ser utilizado por múltiples usuarios del sistema.

## Estructura del Proyecto

El proyecto está organizado en un paquete de Python llamado `app` para separar las responsabilidades y hacer el código más mantenible.

- **`main_app.py`**: El punto de entrada principal. Su única función es iniciar la aplicación.
- **`app/`**: El paquete principal de la aplicación.
  - **`main.py`**: El orquestador de la aplicación. Controla el flujo principal, pero no contiene lógica de negocio detallada.
  - **`database.py`**: Módulo para todas las interacciones con la base de datos PostgreSQL. Contiene la configuración de la conexión, la creación de tablas y todas las funciones CRUD.
  - **`auth.py`**: Gestiona la autenticación de usuarios (inicio de sesión y registro).
  - **`client_management.py`**: Contiene la lógica de negocio para la gestión de clientes (crear, buscar, actualizar, eliminar).
  - **`user_interface.py`**: Responsable de toda la salida a la consola que ve el usuario (menús, mensajes formateados, etc.).
  - **`utils.py`**: Funciones de utilidad reutilizables, como la limpieza de entradas de usuario.
- **`app_log.log`**: Archivo de registro que guarda información sobre las operaciones de la base de datos y posibles errores.

## Cómo Ejecutar la Aplicación

1.  Asegúrate de tener Python 3 y `psycopg` instalados.
2.  Verifica que los datos de conexión en `app/database.py` sean correctos para tu servidor de PostgreSQL.
3.  Desde el directorio raíz (`gestor_clientes/`), ejecuta el siguiente comando en tu terminal:

    ```bash
    python3 main_app.py
    ```

Esto iniciará la aplicación en la consola.
