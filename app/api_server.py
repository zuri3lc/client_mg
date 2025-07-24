#archivo api para entrada al servidor
from fastapi import FastAPI, Depends, HTTPException
from typing import List, Optional
from .api import (
    auth_router,
    clients_router
    )

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

