from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Optional

# MongoDB Configuration
client = MongoClient("mongodb://localhost:27017/")
db = client.mydatabase
wishlist_collection = db.wishlists

# Define Pydantic Models
class WishList(BaseModel):
    user_id: str
    name: str
    books: List[str] = []

class AddBookRequest(BaseModel):
    book_title: str

# Initialize APIRouter
router = APIRouter()

# Create Wishlist
@router.post("/wishlist/", response_model=dict)
def create_wishlist(wishlist: WishList):
    if wishlist_collection.find_one({"user_id": wishlist.user_id}):
        raise HTTPException(status_code=400, detail="Wishlist already exists for this user.")
    wishlist_collection.insert_one(wishlist.dict())
    return {"message": "Wishlist created successfully"}

# Retrieve Wishlist
@router.get("/wishlist/{user_id}", response_model=WishList)
def get_wishlist(user_id: str):
    wishlist = wishlist_collection.find_one({"user_id": user_id})
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")
    return WishList(**wishlist)

# Add Book to Wishlist
@router.post("/wishlist/{user_id}/add_book", response_model=dict)
def add_book_to_wishlist(user_id: str, book_request: AddBookRequest):
    result = wishlist_collection.update_one(
        {"user_id": user_id},
        {"$addToSet": {"books": book_request.book_title}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Wishlist not found or book already added")
    return {"message": "Book added to wishlist"}

# Delete Wishlist
@router.delete("/wishlist/{user_id}", response_model=dict)
def delete_wishlist(user_id: str):
    result = wishlist_collection.delete_one({"user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Wishlist not found")
    return {"message": "Wishlist deleted successfully"}
