from pydantic import BaseModel,EmailStr, HttpUrl,SecretStr
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

class UserLogin(BaseModel):
    username:str
    password:str
 

class UserProfileUpdate(BaseModel):
    username: str = None
    email: EmailStr = None
    pic: HttpUrl = None
    password: SecretStr = None