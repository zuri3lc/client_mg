#moldes
from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import List, Optional

#---- ESQUEMAS PARA MOVIMIENTOS ----
class MovimientoCreateSchema(BaseModel):
    """Esquema para registrar un movimiento"""
    monto: Decimal

class MovimientoShowSchema(BaseModel):
    """Esquema para mostrar movimientos"""
    id: int
    fecha_movimiento: date
    tipo_movimiento: str
    monto: Decimal
    saldo_anterior: Decimal
    saldo_final: Decimal
    
    class Config:
        from_attributes = True

#----- ESQUEMAS PARA CLIENTES ----

class ClientBaseSchema(BaseModel):
    """Molde base, datos que siempre se piden"""
    nombre: str 
    telefono: Optional[str] = None
    ubicacion_aproximada: Optional[str] = None
    foto_domicilio: Optional[str] = None
    comentario: Optional[str] = None
    
class ClientCreateSchema(ClientBaseSchema):
    """hereda todos los datos de la clase base y le añadimos el saldo inicial"""
    saldo_inicial: Decimal 
    
class ClientUpdateSchema(BaseModel):
    """Molde para la actualizacion de clientes"""
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    ubicacion_aproximada: Optional[str] = None
    foto_domicilio: Optional[str] = None
    comentario: Optional[str] = None
    estado_cliente: Optional[str] = None

class ClientUpdateStatusSchema(BaseModel):
    """Molde para actualizar el estado de un cliente"""
    estado_cliente: str

class ClientShowSchema(ClientBaseSchema):
    """Molde para mostrar clientes"""
    id: int
    estado_cliente: str
    fecha_adquisicion: date
    fecha_ultima_modificacion: date
    saldo_actual: Decimal
    
    class Config:
        from_attributes = True

class ClientDetailSchema(ClientShowSchema):
    """Molde compuesto, hereda toda la informacion de ClientShowSchema y le añade una lista de sus movimientos"""
    movimientos_recientes: List[MovimientoShowSchema] = []

#---- ESQUEMAS PARA USUARIOS ----)

#---- ESQUEMAS PARA USUARIOS ----

class UserBase(BaseModel):
    """
    Molde base para un usuario. Solo contiene el username.
    """
    username: str

class User(UserBase):
    """
    Molde para MOSTRAR un usuario. Hereda el username
    y añade el 'id' que viene de la base de datos.
    Nuestra función 'get_current_user' usará este molde.
    """
    id: int
    nombre: Optional[str] = None # Hacemos el nombre opcional
    
    class Config:
        from_attributes = True

#FASTapi espera un JSON con "username" y "password"
class UserLoginSchema(BaseModel):
    username: str
    password: str
#La respuesta que la app espera un JSON "acces_token" y "toke_type"
class TokenSchema(BaseModel):
    access_token: str
    token_type: str



