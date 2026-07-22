from fastapi import Depends, FastAPI, HTTPException, Query, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import models
from typing import Annotated, Optional
from starlette import status
from database import SessionLocal
from models import Items
from database import engine

app = FastAPI(title="Inventory Management API")

models.Base.metadata.create_all(bind=engine)

class ItemCreate(BaseModel):
    # TODO: name, category, price, quantity, description
    name: str = Field(min_length=2, max_length=50)
    category: str
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    description:str | None = Field(description='Description is optional', max_length=200, default=None)


# class Item():
#     def __init__(self, id: int ,name: str, category: str, price: int, quantity: int, description: str):
#         self.id: int = id
#         self.name: str = name
#         self.category: str = category
#         self.price: float = price
#         self.quantity: int = quantity
#         self.description: str = description


# items: dict[int, Item] = {}
# _next_id = 1
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
     db.close()

db_dependeny = Annotated[Session, Depends(get_db)]


# def _get_or_404(item_id:int) -> Item:
#     item = items.get(item_id)
#     if item is None:
#         raise HTTPException(status_code=404, detail='Id not found')
#     return item


@app.get("/items", status_code=status.HTTP_200_OK)
def get_items(db: db_dependeny,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: Optional[bool] = False,
    search: Optional[str] = None,
):
    working_list = db.query(Items).all()
    if category is not None:
        working_list = list(filter(lambda item: item.category.casefold() == category.casefold(), working_list))
    if min_price is not None:
        working_list = list(filter(lambda item: item.price >= min_price, working_list))
    if max_price is not None:
        working_list = list(filter(lambda item: item.price <= max_price, working_list))
    if in_stock_only:
        working_list = list(filter(lambda item: item.quantity > 0, working_list))
    if search is not None:
        working_list = list(filter(lambda item: search.casefold() in item.name.casefold(), working_list))
    return working_list



@app.get("/items/{item_id}", status_code=status.HTTP_200_OK)
def get_item(db: db_dependeny, item_id: int):
    requested_item = db.query(Items).filter(Items.id == item_id).first()
    if requested_item is None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='item not found')
    return requested_item


@app.post("/items",status_code=status.HTTP_201_CREATED)
def create_item(db: db_dependeny, item: ItemCreate):
    item_model = Items(**item.model_dump())

    db.add(item_model)
    db.commit()


@app.put("/items/{item_id}", status_code=status.HTTP_202_ACCEPTED)
def update_item(db: db_dependeny, item_id: int, updated_item: ItemCreate):
    requested_item = db.query(Items).filter(Items.id == item_id).first()
    if requested_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='item not found')
    
    requested_item.name = updated_item.name
    requested_item.category = updated_item.category
    requested_item.price = updated_item.price
    requested_item.quantity = updated_item.quantity
    requested_item.description = updated_item.description

    db.add(requested_item)
    db.commit()


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(db: db_dependeny, item_id: int):
    requested_item = db.query(Items).filter(Items.id == item_id).first()
    if requested_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='item not found')
    db.query(Items).filter(Items.id == item_id).delete()
    db.commit()