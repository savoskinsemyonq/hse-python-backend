from typing import Optional

from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False


class ItemCart(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool


class Cart(BaseModel):
    id: int
    items: list[ItemCart] = []
    price: float = 0
    quantity: int = 0


class CreateItem(BaseModel):
    name: str
    price: float

    model_config = {
        "extra": "forbid"
    }


class UpdateItem(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    model_config = {
        "extra": "forbid"
    }
