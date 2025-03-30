from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Optional

app = FastAPI()

# MongoDB connection and collection setup
client = MongoClient("mongodb://localhost:27017/")
db = client.bookstore  # assuming the database is 'bookstore'
books_collection = db.books

# Pydantic model for book representation
class Book(BaseModel):
    book_id: int
    book_name: str
    book_description: str
    price: float
    author: str
    genre: str
    publisher: str
    year_published: int
    copies_sold: int
    rating: float

@app.get("/books/genre/{genre}", response_model=List[Book])
def get_books_by_genre(genre: str):
    """
    Retrieve List of Books by Genre
    Logic: Given a specific genre, return a list of books for that genre.
    """
    books = books_collection.find({"genre": genre})
    books_list = [Book(**book) for book in books]
    
    if not books_list:
        raise HTTPException(status_code=404, detail="No books found for this genre")
    
    return books_list

@app.get("/books/top_sellers", response_model=List[Book])
def get_top_sellers():
    """
    Retrieve List of Top Sellers (Top 10 books with the most copies sold)
    Logic: Return the top 10 books that have sold the most copies in descending order.
    """
    top_sellers = books_collection.find().sort("copies_sold", -1).limit(10)
    top_sellers_list = [Book(**book) for book in top_sellers]
    
    return top_sellers_list

@app.get("/books/rating/{rating}", response_model=List[Book])
def get_books_by_rating(rating: float):
    """
    Retrieve List of Books for a particular rating and higher
    Logic: Filter by rating higher or equal to the passed rating value.
    """
    books = books_collection.find({"rating": {"$gte": rating}})
    books_list = [Book(**book) for book in books]
    
    if not books_list:
        raise HTTPException(status_code=404, detail="No books found with this rating or higher")
    
    return books_list

@app.patch("/books/discount/{publisher}", response_model=None)
def apply_discount(publisher: str, discount_percent: float):
    """
    Discount books by publisher
    Logic: Update the price of all books under a publisher by a discount percent.
    """
    if discount_percent < 0 or discount_percent > 100:
        raise HTTPException(status_code=400, detail="Discount percentage must be between 0 and 100")
    
    discount_factor = 1 - (discount_percent / 100)
    
    result = books_collection.update_many(
        {"publisher": publisher},
        {"$mul": {"price": discount_factor}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="No books found for this publisher")
    
    return {"message": f"Discount of {discount_percent}% applied to books from {publisher}"}

