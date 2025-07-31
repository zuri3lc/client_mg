from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .schemas import (
    ClientShowSchema,
    ClientCreateSchema,
    ClientUpdateSchema,
    ClientUpdateStatusSchema,
    ClientDetailSchema,
    MovimientoShowSchema,
    MovimientoCreateSchema
    )
from ..database import (
    obtain_clients_db,
    agregar_cliente_db,
    list_client_db,
    client_update_db,
    eliminar_cliente_db,
    historial_movimientos_db,
    actualizar_saldo_db,
    client_search_db
)
from ..security import decode_access_token, oauth2_scheme
from .auth import get_current_user
from . import schemas
#---- ROUTER ----


router = APIRouter(
    prefix="/clients", #todas las rutas de este archivo empezaran con /clients
    tags=["Clientes"]
)

# Endpoint GET (lista) para obtener la lista de clientes de un usuario
@router.get("", response_model=List[ClientShowSchema])
def obtener_clientes_por_usuario(current_user: dict = Depends(get_current_user)):
    """Endpoint para obtener la lista de clientes del usuario autenticado"""
    db_clientes = obtain_clients_db(current_user.id)
    return db_clientes

#Endpoint POST para crear un nuevo cliente
@router.post("/", response_model=ClientShowSchema, status_code=status.HTTP_201_CREATED)
def crear_nuevo_cliente(cliente: ClientCreateSchema, current_user: dict = Depends(get_current_user)):
    """Crea un nuevo cliente en el cuerpo de la peticion, y los valida contra el molde ClientCreateSchema"""
    #cliente.model_dump() convierte el objeto pydantic a un diccionario
    id_nuevo_cliente = agregar_cliente_db(
        **cliente.model_dump(),
        usuario_sistema_id=current_user.id)
    if not id_nuevo_cliente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear cliente, es posible que el nombre ya exista para este usuario"
        )
    cliente_creado = list_client_db(id_nuevo_cliente, current_user.id)
    return cliente_creado

#Endpoint para buscar clientes
@router.get("/search", response_model=List[ClientShowSchema])
def buscar_cliente(query: str, current_user: dict = Depends(get_current_user)):
    """Buscamos clientes por el termino de busqueda"""
    clientes_encontrados = client_search_db(query, current_user.id)
    return clientes_encontrados

#Obtiene la vista detallada de un cliente
@router.get("/{client_id}/details", response_model=ClientDetailSchema)
def obtener_detalle_cliente(client_id: int, current_user: dict = Depends(get_current_user)):
    #1. obtenemos los datos
    cliente = list_client_db(client_id, current_user.id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    #2. obtenemos el historial de movmimientos
    historial_movimientos = historial_movimientos_db(client_id, current_user.id, limite=10)
    
    movimientos_lista = []
    
    if historial_movimientos:
    #3. convertimos las tuplas a diccionario
        columnas = ["id", "fecha_movimiento", "tipo_movimiento", "monto", "saldo_anterior", "saldo_final"]
        lista_de_dicts = [dict(zip(columnas, row[:6])) for row in historial_movimientos]
        movimientos_lista = [schemas.MovimientoShowSchema(**d) for d in lista_de_dicts]
    
        # Pasamos la lista de objetos schema, que ahora sí es del tipo correcto.
        return schemas.ClientDetailSchema(**cliente, movimientos_recientes=movimientos_lista)

#OBTIENE TODOS los movimientos de un cliente
@router.get("/{client_id}/movements", response_model=List[MovimientoShowSchema])
def obtener_movimientos_cliente(client_id: int, current_user: dict = Depends(get_current_user)):
    historial_movimientos = historial_movimientos_db(client_id, current_user.id, limite=25)
    movimientos_lista = []
    if historial_movimientos:
        columnas = ["id", "fecha_movimiento", "tipo_movimiento", "monto", "saldo_anterior", "saldo_final"]
        movimientos_lista = [dict(zip(columnas, row[:6])) for row in historial_movimientos]
    return movimientos_lista

#REGISTRA UN NUEVO MOVIMIENTO
@router.post("/{client_id}/movements", response_model=ClientShowSchema)
def registrar_movimiento(client_id: int, movimiento: MovimientoCreateSchema, current_user: dict = Depends(get_current_user)):
    success = actualizar_saldo_db(client_id, current_user.id, movimiento.monto)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo registrar el movimiento.")
    #movimiento exitoso
    return list_client_db(client_id, current_user.id)



#Endpoint GET para obtener 1 solo cliente
@router.get("/{client_id}", response_model=ClientShowSchema)
def obtener_cliente_por_id(client_id: int, current_user: dict = Depends(get_current_user)):
    """Obtiene los datos de un unico cliente"""
    cliente = list_client_db(client_id, current_user.id)
    if not cliente: #si no se encuentra enviamos un error HTTP
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return cliente

#Endpoint PUT para actualizar un cliente
@router.put("/{client_id}", response_model=ClientShowSchema)
def actualizar_cliente(client_id: int, cliente: ClientUpdateSchema, current_user: dict = Depends(get_current_user)):
    """Endpoint para actualizar un cliente"""
    cliente_actualizado = cliente.model_dump(exclude_unset=True)
    if not cliente_actualizado: #si no se encuentra envuamos un HTTPError
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se enviaron datos para actualizar")
    actualizacion_lista = client_update_db(client_id, current_user.id, **cliente_actualizado)
    if not actualizacion_lista:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    #devolvemos el cliente con los datos actualizados
    return list_client_db(client_id, current_user.id)

#Endpoint que solo actualiza el estado del cliente
@router.put("/{client_id}/status", response_model=schemas.ClientShowSchema, tags=["Clientes"])
def actualizar_estado_cliente(
    client_id: int,
    status_update: schemas.ClientUpdateStatusSchema, # Usamos el molde específico para el estado
    current_user: schemas.User = Depends(get_current_user)
):
    """NUEVO ENDPOINT: Actualiza únicamente el estado de un cliente.
    Es más seguro porque solo permite modificar ese campo específico."""
    success = client_update_db(
        client_id,
        current_user.id,
        estado_cliente=status_update.estado_cliente
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado o error al actualizar el estado."
        )
    # Devolvemos los datos completos del cliente con su nuevo estado.
    return list_client_db(client_id, current_user.id)

#Endpoint DELETE para eliminar un cliente
@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def eliminar_cliente(client_id: int, current_user: dict = Depends(get_current_user)):
    """Endpoint para eliminar un cliente por su id"""
    success = eliminar_cliente_db(client_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    #una eliminacion exitosa no devuelve contenido solo el codigo 204
    return
