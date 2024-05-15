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
    old_password:SecretStr=None

class CarOilInfo(BaseModel):
    car_name: str 
    car_model: int
    odometer_reading: int
    odometer_reading_next: int
    oil_change_date: str
    next_oilChange_date: str
    oil_grade: str
    provider: str
    air_filter:str|None=None
    oil_filter:str|None=None
    ac_filter:str|None=None
    total_cost: int 
    oil_vendor: str|None=None
    notes: str
class LicancePlateInfo(CarOilInfo):
    license_number:str
 
class CarOilInfoUpdater(BaseModel):
    car_name: str|None=None
    car_model: int|None=None
    odometer_reading: int|None=None
    odometer_reading_next: int|None=None
    oil_change_date: str|None=None
    next_oilChange_date: str|None=None
    oil_grade: str|None=None
    provider: str|None=None
    air_filter:str|None=None
    oil_filter:str|None=None
    ac_filter:str|None=None
    total_cost: int|None=None
    oil_vendor: str|None=None
    notes: str|None=None
class LicancePlateInfoUpdater(BaseModel):
    license_number:str 