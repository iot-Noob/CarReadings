from installer import main
from fastapi import APIRouter,Form,Request,Response,HTTPException
from fastapi.requests import  Request
from fastapi.responses import FileResponse,Response,JSONResponse
from createTable import *
import asyncio
from Models import User
from Security import *
from connectDb import RunQuery,db_path 

basicRoutes = APIRouter()
@basicRoutes.on_event('startup')
async def startup_event():
    main()
    print("API IS Starting....")
    await asyncio.gather(UserTable(), OilDateTable(), Licance_Plate())
      

@basicRoutes.post("/login",tags=['User auth  Login'],description="Login accoutn with username and password") 
async def login():
    pass

@basicRoutes.post("/signup", tags=['User auth  Login'], description="Sign up your account")
async def signup(user: User):
    try:
        hp = await get_password_hash(user.password)  # Hash the user's password
        q = await RunQuery("""
            INSERT INTO user (username, password, email, disable, pic) VALUES(?,?,?,?,?)
            """,
            (user.username, hp, user.email, user.disabled, user.pic),
            False,  # sqmq
            False   # rom
        )
        return {"Query sucess account created"}
    except Exception as e:
        raise HTTPException(500, f"Failed to create account: {str(e)}")



 