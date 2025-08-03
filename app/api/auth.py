import os
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from . import schemas
import psycopg

#---Molde y la funcion de verificacion de la db
from .schemas import TokenSchema
from ..database import (
    verificar_credenciales_db,
    db_conection,
    get_user_by_id_db,
    check_username_exist_db,
    registrar_usuario_db,
    
    )
from ..security import create_access_token, decode_access_token, create_refresh_token, oauth2_scheme

#---- ROUTER ----
router = APIRouter(
    prefix="/auth", #todas las rutas de este archivo empezaran con /auth
    tags=["Autenticacion"], #etiqueta para la documentacion
    redirect_slashes=False
)
# Endpoint para el login
# usamos .post() porque el usuario esta enviando datos URL /auth/login
@router.post("/login", response_model=TokenSchema)
def login(
    username: str = Form(...),
    password: str = Form(...)
):

    user_id = verificar_credenciales_db(username, password)
    
    if not user_id:
        #si la funcion devuelve None, credenciales incorrectas
        #la app solo entiende errores http
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales Incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": str(user_id)}
    #se generan ambos tokens
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    #retornamos el token en un diccionario
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user_id
        }

#Endpoint para el refresh token
@router.post("/refresh", response_model=schemas.TokenSchema)
def refresh_token(current_user: schemas.User = Depends(get_user_by_id_db)):
    """Genera un nuevo par de tokens, a partir del token valido"""
    user_id = current_user.id
    token_data = {"sub": str(user_id)}
    
    #nuevo par de tokens
    new_access_token = create_access_token(data=token_data)
    new_refresh_token = create_refresh_token(data=token_data)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user_id": user_id
    }

#-- REGISTRA UN NUEVO USUARIO
@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Autenticacion"])
def register_user(user: schemas.UserCreateSchema, db: psycopg.Connection = Depends(db_conection)):
    # 1. obtenermos la masterkey del .env
    SECRET_KEY = os.getenv("MASTER_KEY")
    # 2. verificacion
    if user.master_key != SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La llave maestra no es valida, no estas autorizado a crear usuarios"
        )
    if check_username_exist_db(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El nombre de usuario {user.username} ya existe"
        )
    user_id = registrar_usuario_db(
        username=user.username,
        password=user.password,
        nombre=user.nombre
    )
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo crear el usuario."
        )
    new_user_data = get_user_by_id_db(user_id)
    db.close()
    return new_user_data


def get_current_user(token: str = Depends(oauth2_scheme), db: psycopg.Connection = Depends(db_conection)) -> schemas.User:
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    
    user_data = get_user_by_id_db(user_id)
    db.close() # Cerramos la conexión que nos dio get_db
    
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        
    return schemas.User(**user_data)