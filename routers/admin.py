from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import models
from typing import Annotated, Optional
from starlette import status
from database import SessionLocal
from models import Items
from enum import Enum
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependeny = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/items', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependeny, user: user_dependency):
    if not user.get('role') == 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does't have access")
    return db.query(Items).all()

@router.get('/items/{item_id}', status_code=status.HTTP_200_OK)
async def get_item(db: db_dependeny, user: user_dependency, item_id: int = Path(gt=0)):
    if not user.get('role') == 'admin':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does't have access")
    requested_item = db.query(Items).filter(Items.id == item_id).first()
    if requested_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does't have access")
    return requested_item