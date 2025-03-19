from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

#MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client.mydatabase
collection = db.users

#User and Credit Card Models
class User(BaseModel):
    username: str
    password: str
    name: Optional[str] = None
    email: Optional[str] = None
    home_address: Optional[str] = None

class CreditCard(BaseModel):
    card_number: str
    expiration_date: str
    cvv: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    name: Optional[str] = None
    home_Address: Optional[str] = None

#Initialize FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI MongoDB API! This is the profile-management branch ;)"}


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

@app.put("/users/{username}", response_model=None)
def update_user(username: str, user_update: UserUpdate):
    update_data = user_update.dict(exclude_unset=True)
    if 'email' in update_data:
        update_data.pop('email')  #Exclude email from update
    result = db.users.update_one(
        {"username": username},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no updates made")
    return {"message": "User updated successfully"}

@app.post("/users/{username}/credit_cards/", response_model=None)
def create_credit_card(username: str, credit_card: CreditCard):
    credit_card_dict = credit_card.dict()
    credit_card_dict['username'] = username
    
    try:
        db.credit_cards.insert_one(credit_card_dict)
        return {"message": "Credit card created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))