# Versión 6 - La estándar de la industria

FROM python:3.12-slim

WORKDIR /app

# 1. Copiamos los requisitos primero
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copiamos TODO el código de nuestro proyecto
COPY . .

# 3. --- EL PASO MÁGICO ---
#    'pip install -e .' le dice a pip que instale el proyecto
#    que se encuentra en el directorio actual (gracias al setup.py)
#    en modo "editable". Esto hace que Python conozca todas
#    las rutas y módulos de nuestra app sin lugar a dudas.
RUN pip install -e .

# 4. Exponemos el puerto
EXPOSE 8000

# 5. El comando de ejecución no cambia de nuestra versión 4,
#    que ya era la correcta.
CMD ["uvicorn", "app.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
