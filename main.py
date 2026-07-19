from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI(title="Inventory Management API")

class ItemCreate(BaseModel):
    # TODO: name, category, price, quantity, description
    id: int | None = Field(description='ID in not needed', default=None)
    name: str = Field(min_length=2, max_length=50)
    category: str
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    description:str | None = Field(description='Description is optional', max_length=200, default=None)


class Item():
    def __init__(self, id: int ,name: str, category: str, price: int, quantity: int, description: str):
        self.id: int = id
        self.name: str = name
        self.category: str = category
        self.price: float = price
        self.quantity: int = quantity
        self.description: str = description


items: dict[int, Item] = {}
_next_id = 1

def _get_or_404(item_id:int) -> Item:
    item = items.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='Id not found')
    return item


@app.get("/items", status_code=status.HTTP_200_OK)
def get_items(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: Optional[bool] = None,
    search: Optional[str] = None,
):
    working_list = list(items.values())
    if category is not None:
        working_list = list(filter(lambda item: item.category.casefold() == category.casefold(), working_list))
    if min_price is not None:
        working_list = list(filter(lambda item: item.price > min_price, working_list))
    if max_price is not None:
        working_list = list(filter(lambda item: item.price < max_price, working_list))
    if in_stock_only is not None:
        working_list = list(filter(lambda item: item.quantity > 0, working_list))
    if search is not None:
        working_list = list(filter(lambda item: search.casefold() in item.name.casefold(), working_list))
        
    return working_list



@app.get("/items/{item_id}", status_code=status.HTTP_200_OK)
def get_item(item_id: int):
    return _get_or_404(item_id)


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    global _next_id
    new_item = Item(**item.model_dump())
    new_item.id = _next_id
    _next_id += 1
    items[new_item.id] = new_item
    return new_item


@app.put("/items/{item_id}", status_code=status.HTTP_200_OK)
def update_item(item_id: int, updated_item: ItemCreate):
    _get_or_404(item_id)
    new_item = Item(**updated_item.model_dump())
    new_item.id = item_id
    items[item_id] = new_item
    return new_item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    _get_or_404(item_id)
    items.pop(item_id)


# ---------------------------------------------------------------------------
# BONUS (only after 1-6 work): PATCH /items/{item_id} — partial update
# ---------------------------------------------------------------------------
# class ItemUpdate(BaseModel):
#     name: Optional[str] = None
#     category: Optional[str] = None
#     price: Optional[float] = None
#     quantity: Optional[int] = None
#     description: Optional[str] = None
#
# @app.patch("/items/{item_id}")
# def partial_update_item(item_id: int, patch: ItemUpdate):
#     # TODO: use patch.model_dump(exclude_unset=True) to see what was
#     # actually sent, then only update those fields.
#     pass
