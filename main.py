from typing import Annotated, Optional

import pymongo
from fastapi import FastAPI, Body
from pydantic import BaseModel, BeforeValidator, Field, ConfigDict
from pydantic_core.core_schema import json_schema
from pymongo.server_api import ServerApi
import motor.motor_asyncio
import pydantic


#path to the DB
app = FastAPI(
    title="Book Ratings & Reviews",
    summary="A way to rate and review books"
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

class Book(BaseModel):
    id:Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str = Field(...)
    author: str = Field(...)
    rating: float = Field()
    comments: Optional[str] = Field()
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": PyObjectId,
                "title": "The Awakening",
                "author": "Kate Chopin",
                "rating": 3.0,
                "comments": "",
            }
        }
    )

class UpdateBook(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
