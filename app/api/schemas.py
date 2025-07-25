#moldes
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

#FASTapi espera un JSON con "username" y "password"
class UserLoginSchema(BaseModel):
    username: str
    password: str
#La respuesta que la app espera un JSON "acces_token" y "toke_type"
class TokenSchema(BaseModel):
    access_token: str
    token_type: str

#Molde base, datos que siempre se piden
class ClientBaseSchema(BaseModel):
    nombre: str #campo obligatorio
    telefono: Optional[str] = None #campo opcional
    ubicacion: Optional[str] = None #campo opcional
    foto_domicilio: Optional[str] = None #campo opcional por ahora solo sera una cadena
    comentario: Optional[str] = None #campo opcional 
    
#Molde para los datos que se requieren para CREAR un cliente
class ClientCreateSchema(ClientBaseSchema): #hereda los campos del molde base
    saldo_inicial: Decimal #añadimos un campo mas, este es obligatorio

#Molde para MOSTRAR datos
#hereda los campos del monde base y añadimos los campos que genera la DB
class ClientShowSchema(ClientBaseSchema):
    id: int
    fecha_adquisicion: date
    fecha_ultima_modificacion: date
    saldo_actual: Decimal
    estado_cliente: str
    usuario_sistema_id: int
    #esta configuracion es un traductor que le dice a Pydantic que puede construirlo no solo desde un diccionario si no despues de un objeto complejo, en este caso la respuesta de ls DB
    class Config:
        from_attributes = True

#Molde para actualizar un cliente
class ClientUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    ubicacion: Optional[str] = None
    foto_domicilio: Optional[str] = None
    comentario: Optional[str] = None
    estado_cliente: Optional[str] = None







