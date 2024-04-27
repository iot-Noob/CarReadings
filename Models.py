from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    disabled: Optional[bool] = False     
    pic: Optional[str] = None
 

class TokenData(BaseModel):
    username: str | None = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

 