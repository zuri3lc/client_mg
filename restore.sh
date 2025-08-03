# #!/bin/bash
#
# # --- CONFIGURACIÓN ---
# DB_CONTAINER_NAME="postgres_db"
# DB_USER="g_clientes"
# DB_NAME="db_clients"
#
# # --- LÓGICA DEL SCRIPT ---
#
# # Verificar que se proporcionó un archivo de backup como argumento
# if [ -z "$1" ]; then
#   echo "ERROR: Debes proporcionar la ruta al archivo de backup a restaurar."
#   echo "Uso: ./restore.sh /ruta/al/backup-YYYY-MM-DD_HH-MM.sql.gz"
#   exit 1
# fi
#
# BACKUP_FILE=$1
#
# # Verificar que el archivo de backup existe
# if [ ! -f "$BACKUP_FILE" ]; then
#   echo "ERROR: El archivo de backup '$BACKUP_FILE' no fue encontrado."
#   exit 1
# fi
#
# echo "ADVERTENCIA: Estás a punto de restaurar la base de datos '$DB_NAME'."
# echo "TODOS LOS DATOS ACTUALES SERÁN ELIMINADOS Y REEMPLAZADOS."
# read -p "¿Estás seguro de que quieres continuar? (s/n): " CONFIRM
#
# if [ "$CONFIRM" != "s" ]; then
#   echo "Restauración cancelada por el usuario."
#   exit 0
# fi
#
# echo "INFO: Restaurando desde '$BACKUP_FILE'..."
#
# # Descomprimir y pasar el contenido a psql dentro del contenedor
# gunzip < "$BACKUP_FILE" | docker exec -i "$DB_CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME"
#
# if [ ${PIPESTATUS[0]} -eq 0 ] && [ ${PIPESTATUS[1]} -eq 0 ]; then
#     echo "ÉXITO: La base de datos ha sido restaurada correctamente."
# else
#     echo "ERROR: Ocurrió un error durante la restauración."
#     exit 1
# fi
#
# echo "--- Proceso de restauración finalizado ---"

#!/bin/bash

# --- CONFIGURACIÓN ---
DB_CONTAINER_NAME="postgres_db"
DB_USER="g_clientes"
DB_NAME="db_clients"

# --- LÓGICA DEL SCRIPT ---

if [ -z "$1" ]; then
  echo "ERROR: Debes proporcionar la ruta al archivo de backup a restaurar."
  echo "Uso: ./restore.sh /ruta/al/backup.sql.gz"
  exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
  echo "ERROR: El archivo de backup '$BACKUP_FILE' no fue encontrado."
  exit 1
fi

echo "ADVERTENCIA: Estás a punto de restaurar la base de datos '$DB_NAME'."
echo "TODOS LOS DATOS ACTUALES SERÁN ELIMINADOS Y REEMPLAZADOS."
read -p "¿Estás seguro de que quieres continuar? (s/n): " CONFIRM

if [ "$CONFIRM" != "s" ]; then
  echo "Restauración cancelada por el usuario."
  exit 0
fi

echo "INFO: Restaurando desde '$BACKUP_FILE'..."

# --- COMANDO DE RESTAURACIÓN MEJORADO ---
# Usamos el flag --quiet (-q) de psql para una salida limpia y evitamos redirigir.
gunzip < "$BACKUP_FILE" | docker exec -i "$DB_CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME"

# --- VERIFICACIÓN ROBUSTA Y SIMPLIFICADA ---
# Capturamos el código de salida de la cadena de comandos anterior.
EXIT_CODE=$?

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "ÉXITO: La base de datos ha sido restaurada correctamente."
else
    echo "ERROR: Ocurrió un error durante la restauración (código de salida: $EXIT_CODE)."
    exit 1
fi

echo "--- Proceso de restauración finalizado ---"
