from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
#---Molde y la funcion de verificacion de la db
from .schemas import TokenSchema
from ..database import verificar_credenciales_db
from ..security import create_access_token

#---- ROUTER ----
router = APIRouter(
    prefix="/auth", #todas las rutas de este archivo empezaran con /auth
    tags=["Autenticacion"] #etiqueta para la documentacion
)
# Endpoint para el login
# usamos .post() porque el usuario esta enviando datos URL /auth/login
@router.post("/login", response_model=TokenSchema)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint para el login, recibe usuario y contraseña y devuelve un token"""
    #reutilizamos la funcion que ya hemos utilizado
    user_id = verificar_credenciales_db(form_data.username, form_data.password)
    
    if not user_id:
        #si la funcion devuelve None, credenciales incorrectas
        #la app solo entiende errores http
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales Incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    #si las credenciales son correctas
    #creamos el payload del token
    #'sub' (subject) es el estandar para el identificador del usuario
    token_data = {"sub": str(user_id)}
    
    #llamamos a la funcion para crear el token
    access_token = create_access_token(data=token_data)
    #retornamos el token en un diccionario
    return {"access_token": access_token, "token_type": "bearer"}

