from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class RoleEnum(str, Enum):
    Manager = 'manager'
    ADMIN = 'admin'
    VIEWER = 'viewer'

class CategoryEnum(str, Enum):
    Electronics = 'Electronics'
    Furniture = 'Furniture'
    Clothing = 'Clothing'
    Food_Beverage = 'Food_Beverage'
    Tools = 'Tools'
    Office_Supplies = 'Office_Supplies'
    Health_Beauty = 'Health_Beauty'
    Toys_Games =  'Toys_Games'
    Books_Media = 'Books_Media'
    Automotive = 'Automotive'
    Sporting_Goods = 'Sporting_Goods'
    Home_Kitchen = 'Home_Kitchen'

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool

    model_config=ConfigDict(
        from_attributes=True
    )


class UserCreate(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: RoleEnum


class ItemCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    category: CategoryEnum
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    description:str | None = Field(description='Description is optional', max_length=200, default=None)


class ItemResponse(BaseModel):
    id: int
    name: str
    category: CategoryEnum
    price: float
    quantity: int
    description: str | None

    model_config=ConfigDict(
        from_attributes=True
    )