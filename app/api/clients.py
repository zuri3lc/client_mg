from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .schemas import ClientShowSchema, ClientCreateSchema
from ..database import (
    obtain_clients_db,
    agregar_cliente_db,
    list_client_db
)


router = APIRouter(
    prefix="/clients", #todas las rutas de este archivo empezaran con /clients
    tags=["Clientes"]
)

# Endpoint par obtener la lista de clientes de un usuario
@router.get("/", response_model=List[ClientShowSchema])
def obtener_clientes_por_usuario():
    """Endpoint para obtener la lista de clientes de un usuario"""
    #por ahora indicamos un ID de usuario fijo
    user_id = 2
    db_clientes = obtain_clients_db(user_id)
    #pydantic, usara el molde ClienteShowSchema y from_attributes, para convertir los resultados de la DB al formatos JSON correcto
    return db_clientes

#Endpoint para crear un nuevo cliente
@router.post("/", response_model=ClientShowSchema, status_code=status.HTTP_201_CREATED)
def crear_nuevo_cliente(cliente: ClientCreateSchema):
    """Crea un nuevo cliente en el cuerpo de la peticion, y los valida contra el molde ClientCreateSchema"""
    user_id = 2
    #llamamos a la funcion de DB, pasandole los datos del molde.
    #cliente.model_dump() convierte el objeto pydantic a un diccionario
    id_nuevo_cliente = agregar_cliente_db(
        **cliente.model_dump(),
        usuario_sistema_id=user_id)
    #validamos los fallos
    if not id_nuevo_cliente:
        #si hubo un error, por lo que sea, un duplicado o un error en la db
        #lanzamos un error HTTP
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear cliente, es posible que el nombre ya exista para este usuario"
        )
    #si el cliente se creo con exito, obtenemos los datos para devolverlos
    cliente_creado = list_client_db(id_nuevo_cliente, user_id)
    return cliente_creado


