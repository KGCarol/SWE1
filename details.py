from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)
db = client["bookstore"]  # database name
books_collection = db["books"]
authors_collection = db["authors"]


class Book(BaseModel):
    book_id: int #the book_id is the book's isbn
    book_name: str
    book_description: str
    price: float
    author: str
    genre: str
    publisher: str
    year_published: int
    copies_sold: int


class Author(BaseModel):
    author_id: int
    first_name: str
    last_name: str
    biography: str
    publisher: str

app = FastAPI()

@app.post("/books/")
def add_book(book: Book):
    books_collection.insert_one(book.model_dump())
    return {"message": "book created successfully"}


@app.get("/books/{book_id}")
def get_book_info(book_id: int):
    book = books_collection.find_one({"book_id": book_id})
    if book is None:
        raise HTTPException(status_code=404, detail="Book could not be found")
    return Book(**book)


@app.post("/authors/")
def add_author(author: Author):
    authors_collection.insert_one(author.model_dump())
    return {"message": "author added successfully"}


@app.get("/authors/{author_id}/books")
def get_books_by_author(author_id:int):
    selected_author = authors_collection.find_one({"author_id" : author_id})
    if selected_author is None:
        raise HTTPException(status_code=404, detail="Author could not be found")
    author_object = Author(**selected_author)
    full_name: str = author_object.first_name + " " + author_object.last_name
    books = books_collection.find({"author": full_name})
    return [Book(**book) for book in books]

