from installer import main
from fastapi import APIRouter,Form,Request,Response,HTTPException
from fastapi.requests import  Request
from fastapi.responses import FileResponse,Response,JSONResponse
from createTable import *
import asyncio
from Models import User,UserLogin,UserProfileUpdate
from Security import *
from connectDb import RunQuery,db_path 

basicRoutes = APIRouter()
@basicRoutes.on_event('startup')
async def startup_event():
    main()
    print("API IS Starting....")
    await asyncio.gather(UserTable(), OilDateTable(), Licance_Plate())
      

@basicRoutes.post("/login", tags=['User auth'], description="Login account with username and password") 
async def login(user_login: UserLogin):
    user_data = await authenticate_user(user_login.username, user_login.password)
    if user_data:
        access_token = await create_access_token(data={"sub": user_data['username'], "user_id": user_data['user_id']})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


@basicRoutes.post("/signup",tags=['User auth'], description="Sign up your account")
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

@basicRoutes.delete("/delete_account",tags=['User auth'],description="Delete account permenently add current username and password to delete as deletion is senstivve  process require auth if you are a real user ",name="Delete account") 
async def delete_account(token:str=Depends(get_current_user),passwd:str=Form(...),username:str=Form(...)):
    dbdata=await RunQuery(q="""SELECT username,password FROM user where id=? """,val=(token['id'],))
    if dbdata:
        dhp=await verify_password(passwd,dbdata[1])
        cuid=token['id']
        if dbdata[0]==username and dhp:
            dq=await RunQuery(q="DELETE   FROM user WHERE id=?",val=(cuid,))
            return {f"Account deletion sucess!! {dq if dq else ""}"}
        else:
            return{"ERROR delete user account username or password not correct"}
    else:
        raise HTTPException(404,"No such user exist to delete.")

@basicRoutes.patch("/update_profile", tags=['User Profile'], description="Update user profile information partially")
async def update_profile(profile_update: UserProfileUpdate, token: str = Depends(get_current_user)):
    try:
        # Construct the update query based on the fields provided in the request
        update_query = "UPDATE user SET"
        update_values = []
        if profile_update.username is not None:
            update_query += " username = ?,"
            update_values.append(profile_update.username)
        if profile_update.email is not None:
            update_query += " email = ?,"
            update_values.append(profile_update.email)
        if profile_update.pic is not None:
            update_query += " pic = ?,"
            update_values.append(str(profile_update.pic))  # Convert URL to string
        if profile_update.password is not None:
            hp = await get_password_hash(profile_update.password.get_secret_value())
            update_query += " password = ?,"
            update_values.append(hp)
        
        # Remove the trailing comma
        update_query = update_query.rstrip(",")

        # Add WHERE clause to ensure the update applies only to the current user
        update_query += " WHERE id = ?"
        update_values.append(token['id'])
        
        # Execute the update query
        await RunQuery(update_query, tuple(update_values))
        
        return {"message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


 