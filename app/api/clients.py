from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .schemas import ClientShowSchema, ClientCreateSchema, ClientUpdateSchema
from ..database import (
    obtain_clients_db,
    agregar_cliente_db,
    list_client_db,
    client_update_db,
    eliminar_cliente_db
)
from ..security import decode_access_token, oauth2_scheme

#--- FUNCION GUARDIA ---
# esta funcion es una dependencia, FASTApi la ejecutara primero
#1. exige un token ('Depends(oauth2_scheme)')
#2. lo valida con decode_access_token
#3. si es valido, devuelve el id del usuario, si no, devuelve error 401
def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    user_id = decode_access_token(token) #decodificamos el token
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user_id
    


router = APIRouter(
    prefix="/clients", #todas las rutas de este archivo empezaran con /clients
    tags=["Clientes"]
)

# Endpoint GET (lista) para obtener la lista de clientes de un usuario
@router.get("/", response_model=List[ClientShowSchema])
def obtener_clientes_por_usuario(user_id: int = Depends(get_current_user_id)):
    """Endpoint para obtener la lista de clientes de un usuario"""
    #por ahora indicamos un ID de usuario fijo
    db_clientes = obtain_clients_db(user_id)
    #pydantic, usara el molde ClienteShowSchema y from_attributes, para convertir los resultados de la DB al formatos JSON correcto
    return db_clientes

#Endpoint POST para crear un nuevo cliente
@router.post("/", response_model=ClientShowSchema, status_code=status.HTTP_201_CREATED)
def crear_nuevo_cliente(cliente: ClientCreateSchema, user_id: int = Depends(get_current_user_id)):
    """Crea un nuevo cliente en el cuerpo de la peticion, y los valida contra el molde ClientCreateSchema"""
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

#Endpoint GET para obtener 1 solo cliente
@router.get("/{client_id}", response_model=ClientShowSchema)
def obtener_cliente_por_id(client_id: int, user_id: int = Depends(get_current_user_id)):
    """Obtiene los datos de un unico cliente"""
    cliente = list_client_db(client_id, user_id)
    if not cliente: #si no se encuentra enviamos un error HTTP
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return cliente

#Endpoint PUT para actualizar un cliente
@router.put("/{client_id}", response_model=ClientShowSchema)
def actualizar_cliente(client_id: int, cliente: ClientUpdateSchema, user_id: int = Depends(get_current_user_id)):
    """Endpoint para actualizar un cliente"""
    #.model_dump(exclude_unset=True) crea un diccionario con los datos que el usuario envio, ignorando los que dejo en blanco
    cliente_actualizado = cliente.model_dump(exclude_unset=True)
    if not cliente_actualizado: #si no se encuentra envuamos un HTTPError
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se enviaron datos para actualizar")
    actualizacion_lista = client_update_db(client_id, user_id, **cliente_actualizado)
    if not actualizacion_lista:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    #devolvemos el cliente con los datos actualizados
    return list_client_db(client_id, user_id)

#Endpoint DELETE para eliminar un cliente
@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def eliminar_cliente(client_id: int, user_id: int = Depends(get_current_user_id)):
    """Endpoint para eliminar un cliente por su id"""
    user_id = 2
    success = eliminar_cliente_db(client_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    #una eliminacion exitosa no devuelve contenido solo el codigo 204
    return


