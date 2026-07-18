"""
Inventory Management API — practice skeleton.

Read PROJECT_BRIEF.md first. Fill in the TODOs yourself — don't skip to
answers. Run with:

    uvicorn main:app --reload

Then test at http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="Inventory Management API")


# ---------------------------------------------------------------------------
# TODO 1: Define your Pydantic model(s)
# ---------------------------------------------------------------------------
# You'll likely want two models:
#   - ItemCreate: what the client sends in POST (no `id` field)
#   - Item: what you store/return (includes `id`)
#
# Remember to use Field() for validation constraints (min_length, gt, ge, etc).
# For `category`, think about whether a plain str with a manual check is
# enough for now, or whether you want to look into Literal / Enum.

class ItemCreate(BaseModel):
    # TODO: name, category, price, quantity, description
    id: int | None = Field(description='ID in not needed', default=None)
    name: str = Field(min_length=2, max_length=50)
    category: str
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    description:str | None = Field(description='Description is optional', max_length=200, default=None)


class Item(): # I Deleted the parent class
    def __init__(self, id: int ,name: str, category: str, price: int, quantity: int, description: str):
        self.id: int = id
        self.name: str = name
        self.category: str = category
        self.price: float = price
        self.quantity: int = quantity
        self.description: str = description


# ---------------------------------------------------------------------------
# In-memory "database"
# ---------------------------------------------------------------------------
items: list[Item] = []
def create_id(item):
    item.id = 1 if len(items) == 0 else items[-1].id + 1
    return item


# ---------------------------------------------------------------------------
# TODO 2: GET /items — list with optional filters
# ---------------------------------------------------------------------------
@app.get("/items")
def get_items(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: Optional[bool] = None,
    search: Optional[str] = None,
):
    # TODO: start with `items`, then narrow the list down based on
    # whichever query params were actually provided (not None).
    working_list = items
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



# ---------------------------------------------------------------------------
# TODO 3: GET /items/{item_id} — single item
# ---------------------------------------------------------------------------
@app.get("/items/{item_id}")
def get_item(item_id: int):
    # TODO: find the item with this id.
    # If it doesn't exist: raise HTTPException(status_code=404, detail=...)
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Id not found")


# ---------------------------------------------------------------------------
# TODO 4: POST /items — create
# ---------------------------------------------------------------------------
@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    # TODO:
    #   1. build a new Item using item.model_dump() + the next id
    #   2. append it to `items`
    #   3. increment your id counter
    #   4. return the created item
    new_item = Item(**create_id(item).model_dump())
    items.append(create_id(new_item))
    return new_item


# ---------------------------------------------------------------------------
# TODO 5: PUT /items/{item_id} — full update
# ---------------------------------------------------------------------------
@app.put("/items/{item_id}")
def update_item(item_id: int, updated_item: ItemCreate):
    # TODO: find the item, replace its fields (keep the same id), 404 if missing
    for i in range(len(items)):
        if items[i].id == item_id:
            updated_item.id = item_id
            items[i] = Item(**updated_item.model_dump())
            return updated_item
    raise HTTPException(status_code=404, detail="id not found")
# ---------------------------------------------------------------------------
# TODO 6: DELETE /items/{item_id}
# ---------------------------------------------------------------------------
@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    # TODO: find and remove the item, 404 if missing
    for i in range(len(items)):
        if items[i].id == item_id:
            items.pop(i)
            return "succes"
    raise HTTPException(status_code=404, detail="id not found")


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
