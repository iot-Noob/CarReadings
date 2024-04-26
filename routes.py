from fastapi import APIRouter,Form
from fastapi.requests import  Request
from fastapi.responses import FileResponse,Response,JSONResponse
from createTable import *
from Security import *
basicRoutes = APIRouter()
 

@basicRoutes.on_event('startup')
async def startup_event():

    print("API IS Starting....")
    UserTable()
    OilDateTable()
    Licance_Plate()        

#Logni account
@basicRoutes.post(path='/login',tags=['Auth method'],name="Login Account",description="Login basic account with username and password and generate JWT")
async def login(username:str=Form(...),password:str=Form(...)):
    try:
        gcu=RunQuery("SELECT * FROM user WHERE username LIKE ?",(username,),True,False)
        if gcu:
            return gcu
        else:
            raise HTTPException(404,"No user found")
    except Exception as e:
        raise HTTPException(500,f"Error login {e} ")
#Signup 

@basicRoutes.post(path='/Signup',tags=['Auth method'],name="Sign up account",description="Basic signup ")
async def login(user:User):
    try:
        pass
    except Exception as e:
        raise HTTPException(500,f"Error login {e} ")