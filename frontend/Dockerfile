# frontend/Dockerfile

# ---- Etapa 1: Construcción (Build Stage) ----
# --- CORRECCIÓN CLAVE ---
# Cambiamos a la imagen 'node:18', que está basada en Debian.
# Es más grande pero mucho más compatible y soluciona errores de criptografía.
FROM node:20-alpine AS build

WORKDIR /app

# Copiamos solo los archivos de dependencias para optimizar la caché de Docker.
COPY package*.json ./

# Instalamos las dependencias.
RUN npm install

# Copiamos el resto del código fuente.
COPY . .

# Ejecutamos el comando de construcción.
RUN npm run build

# ---- Etapa 2: Producción (Production Stage) ----
FROM nginx:stable-alpine

# Copiamos únicamente la carpeta 'dist' (el resultado de la construcción).
COPY --from=build /app/dist /usr/share/nginx/html

# Copiamos la configuración de Nginx.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponemos el puerto 80.
EXPOSE 80

# El comando por defecto de Nginx inicia el servidor.
CMD ["nginx", "-g", "daemon off;"]
