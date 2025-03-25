from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from typing import Optional

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI MongoDB API!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

#MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client.mydatabase
collection = db.users
carts_collection = db.shopping_carts

class User(BaseModel):
    username: str

#current place holder of mine for book to add in shopping cart
class CartItem(BaseModel):
    item_id: str  
    item_name: str
    quantity: int
    price_per_item: float

#actual shopping cart class
class ShoppingCart(BaseModel):
    user_id: str
    items: List[CartItem] = []  

#Initialize FastAPI
app = FastAPI()

@app.post("/users/", response_model=None)
def create_user(user: User):
    db.users.insert_one(user.dict())
    return {"message": "User created successfully"}

@app.get("/users/{username}", response_model=User)
def get_user(username: str):
    user = db.users.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)


@app.post("/users/{username}/shopping_cart/items/", response_model=None)
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


@app.delete("/users/{username}/shopping_cart/items/{item_id}", response_model=None)
def remove_item_from_cart(username: str, item_id: str):
    cart = carts_collection.find_one({"user_id": username})
    
    if not cart:
        raise HTTPException(status_code=404, detail="Shopping cart not found")


    result = carts_collection.update_one(
        {"user_id": username},
        {"$pull": {"items": {"item_id": item_id}}}  # Remove item by item_id
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    return {"message": "Item removed from shopping cart successfully"}


@app.put("/users/{username}/shopping_cart/items/{item_id}", response_model=None)
def update_item_quantity(username: str, item_id: str, quantity: int):
    # Find the user's cart
    cart = carts_collection.find_one({"user_id": username})
    
    if not cart:
        raise HTTPException(status_code=404, detail="Shopping cart not found")

    # Check if the item exists in the cart
    existing_item = next((i for i in cart['items'] if i['item_id'] == item_id), None)

    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    # Update the quantity of the item
    carts_collection.update_one(
        {"user_id": username, "items.item_id": item_id},
        {"$set": {"items.$.quantity": quantity}} 
    )

    return {"message": "Item quantity updated successfully"}


@app.get("/users/{username}/shopping_cart", response_model=ShoppingCart)
def get_shopping_cart(username: str):
    cart = carts_collection.find_one({"user_id": username})

    if not cart:
        raise HTTPException(status_code=404, detail="Shopping cart not found")

    return ShoppingCart(**cart)



    
@app.post("/users/{username}/shopping_cart/", response_model=ShoppingCart)
def create_shopping_cart(username: str):
    user = db.users.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    new_cart = ShoppingCart(user_id=username, items=[])
    carts_collection.insert_one(new_cart.dict())
    
    return new_cart


