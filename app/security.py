import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from dotenv import load_dotenv

#cargamos las variables de entorno para acceder a la clave secreta
load_dotenv()

#CONFIGURACIONES DE SEGURIDAD
#leemos desde el archivo .env 
SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("No se encontro la variable de entorno SECRET_KEY")
#algoritmo para la firma
ALGORITHM = "HS256"
#El tiempo de vida del token
ACCES_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    """crea un token de acceso (JWT)
    args: data (dict): el diccionario con la informacion a codificar (el payload)
    returns: str: el token JWT codificado"""
    #cpiamos los datos para no modificarlos
    to_encode = data.copy()
    #calculamos la fecha de expiracion del token
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCES_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) #exp campo estandar de JWT
    #codificamos el token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) #type: ignore
    return encoded_jwt