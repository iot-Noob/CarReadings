from pydantic import BaseModel,EmailStr, HttpUrl,SecretStr,validator
from typing import Optional,Union
import datetime
import re
class User(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    disabled: Optional[bool] = False     
    pic: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, value):
        # Define the regex pattern for any email domain
        pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if not pattern.match(value):
            raise ValueError('Invalid email format. Must be yourname@domain.com')
        return value

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
    @validator('email')
    def validate_email(cls, value):
        # Define the regex pattern for any email domain
        pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if not pattern.match(value):
            raise ValueError('Invalid email format. Must be yourname@domain.com')
        return value
        

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

    @validator('odometer_reading_next')
    def validate_odometer_reading_next(cls, value, values):
        if 'odometer_reading' in values and value == values['odometer_reading']:
            raise ValueError('Odometer reading next should not be the same as odometer reading')
        return value

    @validator('next_oilChange_date')
    def validate_next_oilChange_date(cls, value, values):
        if 'oil_change_date' in values and value == values['oil_change_date']:
            raise ValueError('Next oil change date should not be the same as oil change date')
        return value
    @validator('next_oilChange_date', 'oil_change_date')
    def validate_date_format(cls, value: Union[str, datetime.date]):
        date_format = re.compile(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4}|\d{2})$')  # Updated regex to accept both dd-mm-yyyy and mm-dd-yyyy
        if not date_format.match(value):
            raise ValueError('Date should be in dd-mm-yyyy   format')
        return value


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
    @validator('odometer_reading_next')
    def validate_odometer_reading_next(cls, value, values):
        if 'odometer_reading' in values and value == values['odometer_reading']:
            raise ValueError('Odometer reading next should not be the same as odometer reading')
        return value

    @validator('next_oilChange_date')
    def validate_next_oilChange_date(cls, value, values):
        if 'oil_change_date' in values and value == values['oil_change_date']:
            raise ValueError('Next oil change date should not be the same as oil change date')
        
    @validator('next_oilChange_date', 'oil_change_date')
    def validate_date_format(cls, value: Union[str, datetime.date]):
        date_format = re.compile(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4}|\d{2})$')  # Updated regex to accept both dd-mm-yyyy and mm-dd-yyyy
        if not date_format.match(value):
            raise ValueError('Date should be in dd-mm-yyyy   format')
        return value
class LicancePlateInfoUpdater(BaseModel):
    license_number: str
    old_license_number: str 
    
    @validator('old_license_number')
    def validate_next_oilChange_date(cls, value, values):
        if 'license_number' in values and value == values['license_number']:
            raise ValueError('License number should not match the old one')
        return value
