# app/api/movements.py
from fastapi import APIRouter, Depends
from typing import List
from . import schemas
from ..database import historial_movimientos_db 
from .auth import get_current_user

router = APIRouter(
    prefix="/movs",
    tags=["Movimientos"]
)

@router.get("/all", response_model=List[schemas.AllMoveSchema])
def sync_all_moves(current_user: schemas.User = Depends(get_current_user)):
    """
    Sincroniza todos los movimientos asociados al usuario autenticado.
    """
    from ..database import sync_movimientos_db
    movimientos = sync_movimientos_db(current_user.id)
    return movimientos