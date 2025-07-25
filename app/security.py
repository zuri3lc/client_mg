import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
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

#esta linea crea un "esquema" de seguridad, le dice a FASTApi que espere un token en el encabezado de la peticion (Authorization Header) con el formato "Bearer <token>". el token apunta a nuestro endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

#FUNCIONES DE SEGURIDAD
def decode_access_token(token: str) -> Optional[int]:
    """Decodifica y valida el token de acceso.
    Args: token (str): el token JWT a validar
    returns: Optional[int]: El ID del usuario si el token es valido, None si no es valido"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticacion invalidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        #intentamos decodificar el token usando el algoritmo y la key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) #type: ignore
        #'sub' ahi se guarda el id del usuario, lo extraemos
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        return int(user_id_str) # retornamos el id del usuario
    except JWTError: #si  ocurre cualquier error durante la decodificacion (token invalido, expirado, firma incorrecta), la libreria lanzara un JWTError
        raise credentials_exception


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




