from installer import main
from fastapi import APIRouter,Form,Request,Response,HTTPException
from fastapi.requests import  Request
from fastapi.responses import FileResponse,Response,JSONResponse
from createTable import *
import asyncio
from Models import User,UserLogin
from Security import *
from connectDb import RunQuery,db_path 

basicRoutes = APIRouter()
@basicRoutes.on_event('startup')
async def startup_event():
    main()
    print("API IS Starting....")
    await asyncio.gather(UserTable(), OilDateTable(), Licance_Plate())
      

@basicRoutes.post("/login", tags=['User auth  Login'], description="Login account with username and password") 
async def login(user_login: UserLogin):
    user_data = await authenticate_user(user_login.username, user_login.password)
    if user_data:
        access_token = await create_access_token(data={"sub": user_data['username'], "user_id": user_data['user_id']})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


@basicRoutes.post("/signup", tags=['User auth  Login'], description="Sign up your account")
async def signup(user: User):
    try:
        hp = await get_password_hash(user.password)  # Hash the user's password
        q = await RunQuery("""
            INSERT INTO user (username, password, email, disable, pic) VALUES(?,?,?,?,?)
            """,
            (user.username, hp, user.email, user.disabled, user.pic),
            False,   
            False    
        )
        return {f"Query sucess account created {q if q else ""}"}
    except Exception as e:
        raise HTTPException(500, f"Failed to create account: {str(e)}")



 