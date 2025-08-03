#archivo api para entrada al servidor
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # 1. middleware de CORS

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from typing import List, Optional
from .api import (
    auth_router,
    clients_router,
    movs_router
    )
from .database import crear_tablas

#1. creamos una instalcia de FASTapi
app = FastAPI(
    title="API gestion de clientes",
    description="Backend de la app offline-first",
    version="1.0.0"
)

# 2. Definimos las conexiones
origins = [
    # "http://localhost:5173",
    # "http://127.0.0.1:5173",
    # "http://192.168.1.87:5173",
    "https://manage.techz.bid" 
]

# 3. Añadimos el middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todas las cabeceras
)

@app.on_event("startup")
def on_startup():
    logging.info("--> Evento de arranque detectado. Verificando y creando tablas...")
    crear_tablas()
    logging.info("--> ¡Verificación de tablas completa! El servidor está listo.")

# 1. Creamos una clase de filtro personalizada.
class No404Filter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return 'GET' in record.getMessage() and 'HTTP/1.1" 404' not in record.getMessage()

logging.getLogger("uvicorn.access").addFilter(No404Filter())

#"Conectamos" el router de auth a la app principal
app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(movs_router)


#2. Definimos nuestro primer "endpoint"
@app.get("/")
def leer_raiz():
    """Endpoint de bienvenida, util para verificar si el servidor esta funcionando"""
    return{"mensaje": "Bienvenido a la API de clientes!"}

