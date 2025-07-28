#archivo api para entrada al servidor
from fastapi import FastAPI, Depends, HTTPException
from typing import List, Optional
from .api import (
    auth_router,
    clients_router
    )
import logging

# --- NUEVO CÓDIGO PARA FILTRAR LOGS ---

# 1. Creamos una clase de filtro personalizada.
#    Hereda de 'logging.Filter' del sistema de logs de Python.
class No404Filter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Esta función se ejecuta para cada línea de log.
        Devuelve 'True' para los logs que queremos mostrar y 'False' para los que queremos ocultar.
        """
        # Verificamos si el mensaje del log contiene la cadena exacta de un error 404 de Uvicorn.
        # Si NO la contiene, lo dejamos pasar (return True).
        # Si SÍ la contiene, lo bloqueamos (return False).
        return 'GET' in record.getMessage() and 'HTTP/1.1" 404' not in record.getMessage()

# 2. Aplicamos nuestro filtro al logger específico de acceso de Uvicorn.
#    Esto asegura que solo filtramos los logs de peticiones HTTP
#    y no otros mensajes importantes del servidor.
logging.getLogger("uvicorn.access").addFilter(No404Filter())

#1. creamos una instalcia de FASTapi
#Es el objeto que manejara las peticiones
app = FastAPI(
    title="API gestion de clientes",
    description="Backend de la app offline-first",
    version="1.0.0"
)
#"Conectamos" el router de auth a la app principal
app.include_router(auth_router)
app.include_router(clients_router)


#2. Definimos nuestro primer "endpoint"
# @app.get("/") le dice a FASTapi que cuando alguien visite la URL raiz "/"
#se debe ejecutar la funcion que esta debajo
@app.get("/")
def leer_raiz():
    """Endpoint de bienvenida, util para verificar si el servidor esta funcionando"""
    return{"mensaje": "Bienvenido a la API de clientes!"}

