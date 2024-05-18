import os
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer,HTTPBearer
from jose import JWTError, jwt
import bcrypt
from models.Models import   User, UserInDB 
from config.connectDb import RunQuery
import datetime

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = bcrypt

http_bearer = HTTPBearer()


async def verify_password(plain_password, hashed_password):
    return pwd_context.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def get_password_hash(password):
    hashed_password = pwd_context.hashpw(password.encode('utf-8'), pwd_context.gensalt())
    return hashed_password.decode('utf-8')

 

async def get_user(username: str):
    user_data = await RunQuery("SELECT username FROM user WHERE username = ?", (username,), sqmq=False, rom=False)
    if not user_data:
        return None  # No user found with the given username
    else:
        return user_data



async def authenticate_user(username: str, password: str):
    user_data = {}
    data = await RunQuery(q="""SELECT username, password, id FROM user WHERE username = ?""", val=(username,), sqmq=False, rom=False)
    if data:
        username = data[0]
        password_from_db = data[1]
        user_id = data[2]
        
        password_verified = await verify_password(password, password_from_db)
        if password_verified:
            user_data['username'] = username
            user_data['user_id'] = user_id
            return user_data
        else:
            raise HTTPException(404, "Username or password not valid. Please make sure you enter valid credentials.")
    else:
        raise HTTPException(404, "Invalid username or password. Please make sure your account exists.")



 

async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

 
async def get_current_user(token: str = Depends(http_bearer)):
    try:
        payload = await decode_jwt(token.credentials)
        if payload is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
        
        expiration_time = payload.get('exp')
        if expiration_time is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has no expiration time")
        
        expiration_datetime = datetime.datetime.fromtimestamp(expiration_time, datetime.timezone.utc)
        if expiration_datetime <= datetime.datetime.now(datetime.timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        
        username: str = payload.get("sub")
        id:str=payload.get("user_id")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username not found in token")
        
        return {"username":username,"id":id}
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
   
        return payload
    except JWTError as e:
        return None

async def user_exist(tokens):
    try:   
        
        cuid = tokens['id']
        cuname=tokens['username']
        cue = await RunQuery(
            q="""SELECT id FROM user WHERE id=? AND username=?  """,
            val=(cuid,cuname  ),
            sqmq=False,
            rom=False
        )
        if cue:
            return True
        else:
            return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while checking user existence: {e}")

