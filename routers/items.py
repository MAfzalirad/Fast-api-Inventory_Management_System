from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import models
from typing import Annotated, Optional
from starlette import status
from database import SessionLocal
from models import Items
from schemas import ItemCreate, CategoryEnum
from .auth import get_current_user

router = APIRouter(
    prefix='/item',
    tags=['item']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependeny = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
def get_items(db: db_dependeny,user: user_dependency,
    category: Optional[CategoryEnum] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: Optional[bool] = False,
    search: Optional[str] = None,
):
    working_list = db.query(Items).filter(Items.owner_id == user.get('id'))
    if category is not None:
        working_list = working_list.filter(Items.category == category)
    if min_price is not None:
        working_list = working_list.filter(Items.price >= min_price)
    if max_price is not None:
        working_list = working_list.filter(Items.price <= max_price)
    if in_stock_only:
        working_list = working_list.filter(Items.quantity > 0)
    if search is not None:
        working_list = working_list.filter(Items.name.ilike(f"%{search}%"))
    working_list = working_list.all()
    return working_list


@router.get("/{item_id}", status_code=status.HTTP_200_OK)
def get_item(db: db_dependeny,user: user_dependency, item_id: int):
    requested_item = db.query(Items).filter(Items.id == item_id).filter(Items.owner_id == user.get('id')).first()
    if requested_item is None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='item not found')
    return requested_item


@router.post("/",status_code=status.HTTP_201_CREATED)
def create_item(db: db_dependeny,user: user_dependency, item: ItemCreate):
    item_model = Items(**item.model_dump(), owner_id = user.get('id'))

    db.add(item_model)
    db.commit()


@router.put("/{item_id}", status_code=status.HTTP_202_ACCEPTED)
def update_item(db: db_dependeny,user: user_dependency, item_id: int, updated_item: ItemCreate):
    requested_item = db.query(Items).filter(Items.id == item_id).filter(Items.owner_id == user.get('id')).first()
    if requested_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='item not found')
    
    requested_item.name = updated_item.name
    requested_item.category = updated_item.category
    requested_item.price = updated_item.price
    requested_item.quantity = updated_item.quantity
    requested_item.description = updated_item.description

    db.add(requested_item)
    db.commit()


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(db: db_dependeny,user: user_dependency, item_id: int):
    requested_item = db.query(Items).filter(Items.id == item_id).filter(Items.owner_id == user.get('id')).first()
    if requested_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='item not found')
    db.query(Items).filter(Items.id == item_id).delete()
    db.commit()