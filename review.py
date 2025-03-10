from typing import Annotated, Optional

import pymongo
from bson import ObjectId
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel, BeforeValidator, Field, ConfigDict, model_validator
from pydantic_core.core_schema import json_schema
from pymongo.server_api import ServerApi
import motor.motor_asyncio
import pydantic


#path to the DB
app = FastAPI(
    title="Book Ratings & Reviews v1",
    summary="A way to rate and review books v1"
)

uri = "mongodb+srv://test1:1tset@swe1-g7.j7sla.mongodb.net/?retryWrites=true&w=majority&appName=SWE1-G7"
client = motor.motor_asyncio.AsyncIOMotorClient(uri)
db = client.reviews

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

PyObjectId = Annotated[str, BeforeValidator(str)]
@app.get("/")
async def root():
    return {"message": "Hello World"}

class Review(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id", description="Unique review ID")
    book_id:str = Field(..., description="ID of the book being reviewed")
    rating:int = Field(..., ge=1, le=5, description="Rating of whole numbers between 1-5")
    comment: Optional[str] = Field(None, description="An optional comment that can be made by users")

    @model_validator(mode='before')
    def set_id(cls, values):
        if "_id" not in values:  # If _id is not provided
            values["_id"] = str(ObjectId())  # Generate a new ObjectId
        return values

model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": str(ObjectId),
                "book_id": "abc123",
                "rating": 5,
                "comment": "Awesome book!",
            }
        }
    )

    #Create a new review
@app.post("/reviews/", response_model=Review)
async def create_review(review : Review):
    review_dict = review.model_dump()
    result = await db.reviews.insert_one(review_dict)
    if result.inserted_id:
        created_review = await db.reviews.find_one({"_id": result.inserted_id})
        return created_review
    raise HTTPException(status_code=500, detail="Review could not be saved")

    #Get reviews for a specific book
@app.get("/reviews/{book_id}", response_model=list[Review])
async def get_reviews(book_id : str):
    if ObjectId.is_valid(book_id):
        book_id = ObjectId(book_id)
    reviews = await db.reviews.find({"book_id": book_id}).to_list(length = 100)
    return reviews

    #Edit an existing review
@app.put("/reviews/{review_id}")
async def update_review(review_id: str, review: Review):
    if not ObjectId.is_valid(review_id):
        raise HTTPException(status_code=400, detail="Invalid review ID format")
    result = await db.reviews.update_one({"_id": ObjectId(review_id)},
        {"$set": review.model_dump(exclude_unset=True)})

    if result.modified_count:
        return {"message": "Review successfully updated"}
    raise HTTPException(status_code=404, detail="Review not found")

@app.delete("/reviews/{review_id}")
async def delete_review(review_id: str):
    if not ObjectId.is_valid(review_id):
        raise HTTPException(status_code=400, detail="Invalid review ID format")
    result = await db.reviews.delete_one({"_id": ObjectId(review_id)})
    if result.deleted_count:
        return {"message": "Review deleted successfully"}
    raise HTTPException(status_code=404, detail="Review not found")