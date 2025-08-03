# #!/bin/bash
#
# # --- CONFIGURACIÓN ---
# # Asegúrate de que estos nombres coincidan con tu docker-compose.yml
# DB_CONTAINER_NAME="postgres_db"
# DB_USER="g_clientes"
# DB_NAME="db_clients"
#
# # Directorio donde se guardarán las copias de seguridad en el servidor
# BACKUP_DIR="/home/zuko/nasdata/client_mg/backup"
#
# # --- LÓGICA DEL SCRIPT ---
#
# # Crear el directorio de backups si no existe
# mkdir -p "$BACKUP_DIR"
#
# # Formato de fecha para el nombre del archivo (Ej: backup-2025-08-02_21-20.sql.gz)
# DATE_FORMAT=$(date "+%m%d-%H%M")
# BACKUP_FILE="$BACKUP_DIR/dump-$DATE_FORMAT.sql.gz"
#
# echo "INFO: Creando backup de la base de datos '$DB_NAME'..."
#
# # Ejecutar pg_dump dentro del contenedor y comprimir la salida
# docker exec "$DB_CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE"
#
# # Verificar si el backup se creó correctamente
# if [ ${PIPESTATUS[0]} -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
#     echo "ÉXITO: Backup creado y guardado en $BACKUP_FILE"
# else
#     echo "ERROR: Falló la creación del backup. Revisar logs."
#     rm -f "$BACKUP_FILE" # Eliminar archivo incompleto si falló
#     exit 1
# fi
#
# # --- LIMPIEZA DE BACKUPS ANTIGUOS ---
# # Mantener solo los 10 backups más recientes
# echo "INFO: Realizando limpieza de backups antiguos..."
# ls -1t "$BACKUP_DIR"/dump-*.sql.gz | tail -n +11 | xargs -r rm
# echo "INFO: Limpieza completada. Se conservan los 10 backups más recientes."
#
# echo "--- Proceso de backup finalizado ---"

#!/bin/bash

# --- CONFIGURACIÓN ---
DB_CONTAINER_NAME="postgres_db"
DB_USER="g_clientes"
DB_NAME="db_clients"

# --- LÓGICA DEL SCRIPT ---

if [ -z "$1" ]; then
  echo "ERROR: Debes proporcionar la ruta al archivo de backup a restaurar."
  echo "Uso: ./restore.sh /ruta/al/backup-YYYY-MM-DD_HH-MM.sql.gz"
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

# --- CAMBIO IMPORTANTE ---
# Redirigimos la salida estándar y de error de psql a /dev/null para una salida limpia.
gunzip < "$BACKUP_FILE" | docker exec -i "$DB_CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1

# Capturamos los códigos de salida en variables para una verificación más segura.
GUNZIP_STATUS=${PIPESTATUS[0]}
PSQL_STATUS=${PIPESTATUS[1]}

# --- VERIFICACIÓN MEJORADA ---
# Comprobamos que ambas variables (ahora sí con valor) sean 0.
if [ "$GUNZIP_STATUS" -eq 0 ] && [ "$PSQL_STATUS" -eq 0 ]; then
    echo "ÉXITO: La base de datos ha sido restaurada correctamente."
else
    echo "ERROR: Ocurrió un error durante la restauración (gunzip: $GUNZIP_STATUS, psql: $PSQL_STATUS)."
    exit 1
fi

echo "--- Proceso de restauración finalizado ---"
