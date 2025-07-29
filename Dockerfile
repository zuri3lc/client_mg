# Versión 7 - Tu Dockerfile con seguridad añadida

FROM python:3.12-slim

WORKDIR /app

# --- PASO 1: CREAR UN USUARIO SEGURO ---
# Creamos un grupo de sistema (-r) llamado 'appgroup' y un usuario de sistema (-r)
# llamado 'appuser' y lo añadimos a ese grupo. Este usuario no tendrá
# privilegios de superusuario (root).
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# --- FIN DEL PASO 1 ---

# Copiamos los requisitos primero (sin cambios)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código de nuestro proyecto (sin cambios)
COPY . .

# 'pip install -e .' (sin cambios)
RUN pip install -e .

# --- PASO 2: ASIGNAR PERMISOS ---
# Cambiamos el propietario de todos los archivos en /app para que pertenezcan
# a nuestro nuevo usuario 'appuser' y a su grupo 'appgroup'.
RUN chown -R appuser:appgroup /app

# --- PASO 3: CAMBIAR DE USUARIO ---
# A partir de esta línea, todos los comandos siguientes se ejecutarán
# como 'appuser', no como 'root'.
USER appuser

# --- FIN DE LOS PASOS DE SEGURIDAD ---

# Exponemos el puerto (sin cambios)
EXPOSE 8000

# El comando de ejecución ahora será lanzado por 'appuser', lo cual es mucho más seguro.
CMD ["uvicorn", "app.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
