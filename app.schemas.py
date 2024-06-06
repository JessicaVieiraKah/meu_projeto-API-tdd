from pydantic import BaseModel
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    price: float

class ProductUpdate(BaseModel):
    name: str = None
    price: float = None

class Product(BaseModel):
    id: int
    name: str
    price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
