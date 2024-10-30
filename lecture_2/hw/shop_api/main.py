from http import HTTPStatus
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Body, Response

from lecture_2.hw.shop_api.models import Cart, ItemCart, Item, CreateItem, UpdateItem

app = FastAPI()

items_db = {}
carts_db = {}

item_id_counter = 0
cart_id_counter = 0


@app.post("/cart", status_code=HTTPStatus.CREATED)
def create_cart(response: Response):
    global cart_id_counter
    cart_id_counter += 1
    cart_id = cart_id_counter
    new_cart = Cart(id=cart_id)
    carts_db[cart_id] = new_cart
    response.headers["location"] = f"/cart/{cart_id}"
    return {"id": cart_id}


@app.get("/cart/{id}")
def get_cart(id: int):
    if id not in carts_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    cart = carts_db[id]
    total_price = 0
    total_quantity = 0
    for cart_item in cart.items:
        item = items_db[cart_item.id]
        if item:
            cart_item.name = item.name
            total_price += item.price * cart_item.quantity
            total_quantity += cart_item.quantity
            cart_item.available = not item.deleted
        else:
            cart_item.available = False
    cart.price = total_price
    cart.quantity = total_quantity
    return cart


@app.get("/cart")
def list_carts(offset: int = Query(0, ge=0), limit: int = Query(10, gt=0),
               min_price: Optional[float] = Query(None, ge=0), max_price: Optional[float] = Query(None, ge=0),
               min_quantity: Optional[int] = Query(None, ge=0), max_quantity: Optional[int] = Query(None, ge=0),
               ):
    carts = list(carts_db.values())
    filter_carts = []
    for cart in carts:
        total_quantity = 0
        total_price = 0
        for cart_item in cart.items:
            item = items_db[cart_item.id]
            if item and not item.deleted:
                total_price += item.price * cart_item.quantity
                total_quantity += cart_item.quantity
        cart.price = total_price
        cart.quantity = total_quantity
        if ((min_price is None or total_price >= min_price) and
                (max_price is None or total_price <= max_price) and
                (min_quantity is None or total_quantity >= min_quantity) and
                (max_quantity is None or total_quantity <= max_quantity)):
            filter_carts.append(cart)
    return filter_carts[offset:offset + limit]


@app.post("/cart/{cart_id}/add/{item_id}")
def add_item_to_cart(cart_id: int, item_id: int):
    if cart_id not in carts_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    if item_id not in items_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    cart = carts_db[cart_id]
    item = items_db[item_id]
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            return {"message": "Item added in cart"}
    cart_item = ItemCart(id=item_id, name=item.name, quantity=1, available=not item.deleted)
    cart.items.append(cart_item)
    return {"message": "Item added in cart"}


@app.post("/item", status_code=HTTPStatus.CREATED)
def create_item(item: CreateItem, response: Response):
    global item_id_counter
    item_id_counter += 1
    item_id = item_id_counter
    new_item = Item(id=item_id, name=item.name, price=item.price, deleted=False)
    items_db[item_id] = new_item
    response.headers["location"] = f"/item/{item_id}"
    return new_item.model_dump()


@app.get("/item/{id}")
def get_item(id: int):
    if id not in items_db or items_db[id].deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return items_db[id].model_dump()


@app.get("/item")
def list_items(offset: int = Query(0, ge=0), limit: int = Query(10, gt=0),
               min_price: Optional[float] = Query(None, ge=0), max_price: Optional[float] = Query(None, ge=0),
               show_deleted: bool = Query(False)
               ):
    items = list(items_db.values())
    filter_items = []
    for item in items:
        if ((show_deleted or not item.deleted) and
                (min_price is None or item.price >= min_price) and
                (max_price is None or item.price <= max_price)):
            filter_items.append(item)
    return [item.model_dump() for item in filter_items[offset:offset + limit]]


@app.put("/item/{id}")
def put_item(id: int, new_item: CreateItem):
    if id not in items_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    item = items_db[id]
    if item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED)
    item.name = new_item.name
    item.price = new_item.price
    return item


@app.patch("/item/{id}")
def patch_item(id: int, item_updates: UpdateItem = Body(default={})):
    if id not in items_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    item = items_db[id]
    if item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED)
    update_data = item_updates.model_dump(exclude_unset=True)
    if "deleted" in update_data:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Field 'deleted' can't changed")
    if not update_data:
        return item
    for key, value in update_data.items():
        setattr(item, key, value)
    return item


@app.delete("/item/{id}")
def delete_item(id: int):
    if id not in items_db:
        return {"message": "Item deleted already"}
    item = items_db[id]
    if item.deleted:
        return {"message": "Item deleted already"}
    item.deleted = True
    return {"message": "Item deleted"}
