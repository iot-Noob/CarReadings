import os
from fastapi import HTTPException, Depends, status
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from Models import Token, TokenData, User, UserInDB
from connectDb import RunQuery

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = bcrypt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_password(plain_password, hashed_password):
    return pwd_context.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def get_password_hash(password):
    hashed_password = pwd_context.hashpw(password.encode('utf-8'), pwd_context.gensalt())
    return hashed_password.decode('utf-8')

 

async def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


async def authenticate_user(fake_db, username: str, password: str):
    user = await get_user(fake_db, username)
    if not user or not await verify_password(password, user.hashed_password):
        return False
    return user


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # Fetch user data from the database
        user_data = await RunQuery("SELECT * FROM user WHERE username = ?", (username,), sqmq=False, rom=True)
        if not user_data:
            raise credentials_exception
        # Convert fetched data into a UserInDB object
        user_dict = dict(user_data[0])
        return UserInDB(**user_dict)
    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        # Handle JWT decoding errors here
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not decode JWT token",
            headers={"WWW-Authenticate": "Bearer"},
        )

 
