#!/bin/bash

# --- CONFIGURACIÓN ---
# Asegúrate de que estos nombres coincidan con tu docker-compose.yml
DB_CONTAINER_NAME="postgres_db"
DB_USER="g_clientes"
DB_NAME="db_clients"

# Directorio donde se guardarán las copias de seguridad en el servidor
BACKUP_DIR="/home/zuko/nasdata/client_mg/backup"

# --- LÓGICA DEL SCRIPT ---

# Crear el directorio de backups si no existe
mkdir -p "$BACKUP_DIR"

# Formato de fecha para el nombre del archivo (Ej: backup-2025-08-02_21-20.sql.gz)
DATE_FORMAT=$(date "+%m%d-%H%M")
BACKUP_FILE="$BACKUP_DIR/backup-$DATE_FORMAT.sql.gz"

echo "INFO: Creando backup de la base de datos '$DB_NAME'..."

# Ejecutar pg_dump dentro del contenedor y comprimir la salida
docker exec "$DB_CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE"

# Verificar si el backup se creó correctamente
if [ ${PIPESTATUS[0]} -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
    echo "ÉXITO: Backup creado y guardado en $BACKUP_FILE"
else
    echo "ERROR: Falló la creación del backup. Revisar logs."
    rm -f "$BACKUP_FILE" # Eliminar archivo incompleto si falló
    exit 1
fi

# --- LIMPIEZA DE BACKUPS ANTIGUOS ---
# Mantener solo los 10 backups más recientes
echo "INFO: Realizando limpieza de backups antiguos..."
ls -1t "$BACKUP_DIR"/backup-*.sql.gz | tail -n +21 | xargs -r rm
echo "INFO: Limpieza completada. Se conservan los 20 backups más recientes."

echo "--- Proceso de backup finalizado ---"
