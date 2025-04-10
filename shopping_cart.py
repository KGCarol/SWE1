from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient


router = APIRouter(prefix="/users", tags=["Shopping Cart"])

client = MongoClient("mongodb://localhost:27017/")
db = client.mydatabase
users_collection = db.users
carts_collection = db.shopping_carts

class CartItem(BaseModel):
    item_id: str
    item_name: str
    quantity: int
    price_per_item: float

class ShoppingCart(BaseModel):
    user_id: str
    items: List[CartItem] = []


@router.post("/{username}/shopping_cart/", response_model=ShoppingCart)
def create_shopping_cart(username: str):
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cart = ShoppingCart(user_id=username, items=[])
    carts_collection.insert_one(cart.dict())
    return cart


@router.post("/{username}/shopping_cart/items/")
def add_item_to_cart(username: str, item: CartItem):
    cart = carts_collection.find_one({"user_id": username})
    if not cart:
        raise HTTPException(status_code=404, detail="Shopping cart not found")

    existing_item = next((i for i in cart['items'] if i['item_id'] == item.item_id), None)

    if existing_item:
        carts_collection.update_one(
            {"user_id": username, "items.item_id": item.item_id},
            {"$inc": {"items.$.quantity": item.quantity}}
        )
    else:
        carts_collection.update_one(
            {"user_id": username},
            {"$push": {"items": item.dict()}}
        )

    return {"message": "Item added to shopping cart successfully"}


@router.delete("/{username}/shopping_cart/items/{item_id}")
def remove_item_from_cart(username: str, item_id: str):
    result = carts_collection.update_one(
        {"user_id": username},
        {"$pull": {"items": {"item_id": item_id}}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    return {"message": "Item removed from shopping cart successfully"}


@router.put("/{username}/shopping_cart/items/{item_id}")
def update_item_quantity(username: str, item_id: str, quantity: int):
    cart = carts_collection.find_one({"user_id": username})
    if not cart:
        raise HTTPException(status_code=404, detail="Shopping cart not found")

    existing_item = next((i for i in cart['items'] if i['item_id'] == item_id), None)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    carts_collection.update_one(
        {"user_id": username, "items.item_id": item_id},
        {"$set": {"items.$.quantity": quantity}}
    )

    return {"message": "Item quantity updated successfully"}


@router.get("/{username}/shopping_cart", response_model=ShoppingCart)
def get_shopping_cart(username: str):
    cart = carts_collection.find_one({"user_id": username})
    if not cart:
        raise HTTPException(status_code=404, detail="Shopping cart not found")
    return ShoppingCart(**cart)
