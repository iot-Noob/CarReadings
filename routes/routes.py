from config.installer import main
from fastapi import APIRouter,Form,Request,Response,HTTPException,Query
from fastapi.requests import  Request
from fastapi.responses import FileResponse,Response,JSONResponse
from config.createTable import *
import asyncio
from models.Models import User,UserLogin,UserProfileUpdate,LicancePlateInfo ,CarOilInfoUpdater,LicancePlateInfoUpdater
from security.Security import *
from config.connectDb import RunQuery,db_path 
from datetime import datetime

basicRoutes = APIRouter()

async def delete_all(token):
    try:
        uid = token['id']
        
        # Delete data from User_License_Plate table
        await RunQuery(
            q="DELETE FROM User_License_Plate WHERE user_id = ?",
            val=(uid,),
            sqmq=False,
            rom=False
        )

        # Delete data from OilEntry table
        await RunQuery(
            q="DELETE FROM OilEntry WHERE license_plate_id IN (SELECT id FROM License_Plate WHERE uid = ?)",
            val=(uid,),
            sqmq=False,
            rom=False
        )

        # Delete data from License_Plate table
        await RunQuery(
            q="DELETE FROM License_Plate WHERE uid = ?",
            val=(uid,),
            sqmq=False,
            rom=False
        )

        # Delete data from Oil_Change table
        await RunQuery(
            q="DELETE FROM Oil_Change WHERE cuid = ?",
            val=(uid,),
            sqmq=False,
            rom=False
        )

        # Delete data from User table
        await RunQuery(
            q="DELETE FROM user WHERE id = ?",
            val=(uid,),
            sqmq=False,
            rom=False
        )

    except Exception as e:
        raise HTTPException(500, f"Failed to delete all data: {e}")



@basicRoutes.on_event('startup')
async def startup_event():
    main()
    print("API IS Starting....")
    await asyncio.gather(UserTable(), OilDateTable(), Licance_Plate(),User_License_Plate(),UserOilEntry(),OilUserRelation())
      

@basicRoutes.post("/login", tags=['User Authentication'], description="Login account with username and password") 
async def login(user_login: UserLogin):
    user_data = await authenticate_user(user_login.username, user_login.password)
    if user_data:
        access_token = await create_access_token(data={"sub": user_data['username'], "user_id": user_data['user_id']})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


@basicRoutes.post("/signup",tags=['User Authentication'], description="Sign up your account")
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

@basicRoutes.delete("/delete_account",tags=['User Authentication'],description="Delete account permenently add current username and password to delete as deletion is senstivve  process require auth if you are a real user ",name="Delete account") 
async def delete_account(token:str=Depends(get_current_user),passwd:str=Form(...),username:str=Form(...)):
    ue=await user_exist(tokens=token)
 
    if not ue:
        raise HTTPException(404,"Invalid token no such user exist")
    
    dbdata=await RunQuery(q="""SELECT username,password FROM user where id=? """,val=(token['id'],))
    if dbdata:
        dhp=await verify_password(passwd,dbdata[1])
        cuid=token['id']
        if dbdata[0]==username and dhp:
            await delete_all(token=token)
            dq=await RunQuery(q="DELETE   FROM user WHERE id=?",val=(cuid,))
            return {f"Account deletion sucess!! {dq if dq else ""}"}
        else:
            return{"ERROR delete user account username or password not correct"}
    else:
        raise HTTPException(404,"No such user exist to delete.")

@basicRoutes.patch("/update_profile", tags=['Account Settings'], description="Update user profile information partially")
async def update_profile(profile_update: UserProfileUpdate, token: str = Depends(get_current_user)):
    try:
        vt=await user_exist(tokens=token)
        if vt==False:
            raise HTTPException(404,"Invalid token no such user exist!!!")
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
            # Verify old password before updating
            pswd_hash = await RunQuery("""SELECT password FROM user WHERE id = ?""", (token['id'],))
            old_password_verified = await verify_password(profile_update.old_password.get_secret_value(), pswd_hash[0])
            
            if old_password_verified:
                # Hash the new password
                hp = await get_password_hash(profile_update.password.get_secret_value())
                update_query += " password = ?,"
                update_values.append(hp)
            else:
                raise HTTPException(status_code=400, detail="Old password does not match")

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

async def Insert_OE(current_id,cln):
    try:
       goid=await RunQuery(q="""
                           SELECT MAX(id) AS latest_oil_id
                            FROM Oil_Change
                            WHERE cuid=?""",val=(current_id,),rom=False,sqmq=False)
       if_le=await RunQuery(q="""
                             SELECT License_Plate.id 
                             FROM License_Plate 
                             INNER JOIN User_License_Plate ON License_Plate.id = User_License_Plate.license_plate_id 
                             WHERE User_License_Plate.user_id = ? 
                             AND License_Plate.license_number =?""",val=(current_id,cln,),rom=False,sqmq=False)
       inoe=await RunQuery(
                        """
                        INSERT INTO OilEntry(license_plate_id,oil_id)
                        VALUES(?,?)
                        """,val=(if_le[0],goid[0]))
        
    except Exception as e:
        raise HTTPException(500,f"Error entry for oil due to ::: {e}")

### Insert data to oil
@basicRoutes.post("/AddOilInfo",tags=['Data Entry endpoint'],name="Oil info add",description="User basic oil info add to database")
async def add_oil_info(add_info:LicancePlateInfo,token:str=Depends(get_current_user)):
    if not await user_exist(tokens=token):
        raise HTTPException(404,"Invalid token no such user exist")
    rq2=None
    try:
        cuid=token['id']

        rq = await RunQuery(
            q=""" INSERT INTO Oil_Change (
                  car_name,
                  car_model,
                  odometer_reading,
                  odometer_reading_next,
                  oil_grade,
                  provider,
                  air_filter,
                  oil_filter,
                  ac_filter,
                  total_cost,
                  oil_vander,
                  oil_change_date,
                  notes,
                  cuid   )
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?)""",
            val=(
                add_info.car_name, 
                add_info.car_model,
                add_info.odometer_reading, 
                add_info.odometer_reading_next, 
                add_info.oil_grade, 
                add_info.provider, 
                add_info.total_cost, 
                add_info.oil_vendor, 
                add_info.air_filter,
                add_info.oil_filter,
                add_info.ac_filter,
                add_info.oil_change_date,
                add_info.notes,
                cuid
            ),
            sqmq=False,
            rom=False
        )

        goid = await RunQuery(
            q="""SELECT MAX(id) AS latest_oil_id
                FROM Oil_Change
                WHERE cuid=? """,
            val=(cuid,),
            sqmq=False,
            rom=False  # Corrected to True to return the result as a list of dictionaries
        )
        
        iuor=await RunQuery(q="""INSERT INTO UserOil(oil_id,user_id) VALUES (?,?)""",val=(goid[0],cuid),sqmq=False,rom=False)
        

        if_le=await RunQuery(q="""
                             SELECT License_Plate.id 
                             FROM License_Plate 
                             INNER JOIN User_License_Plate ON License_Plate.id = User_License_Plate.license_plate_id 
                             WHERE User_License_Plate.user_id = ? 
                             AND License_Plate.license_number =?;
                             """,val=(cuid,add_info.license_number))
        if if_le:
             await Insert_OE(cuid,add_info.license_number)
        if not if_le:
            print(f"NEWLY ENTER DATA OIL ID :::: ",goid[0])
            rq2 = await RunQuery(
                q="""INSERT INTO License_Plate (license_number, uid)
                    VALUES (?, ?);""",
                val=(add_info.license_number, cuid),  
                sqmq=False,
                rom=False
                )
            licance_id=await RunQuery(q="""
                                   SELECT LP.id
                                   FROM License_Plate LP
                                   JOIN UserOil UO ON LP.uid = UO.user_id
                                   JOIN Oil_Change OC ON UO.oil_id = OC.id
                                   WHERE UO.user_id = ?
                                   ORDER BY LP.id DESC
                                   LIMIT 1
                                   """,
                                        val=(cuid,),rom=False,sqmq=False
                                    )
 
            iulp = await RunQuery(
                q="INSERT INTO User_License_Plate (user_id, license_plate_id) VALUES (?, ?)",
                val=(cuid, licance_id[0]),  # Accessing the 'id' field from the dictionary
                sqmq=False,
                rom=False
            )
            await Insert_OE(cuid,add_info.license_number)
  
        return {f"Data insert sucess ":f"Entery sucessful {"Oil insert error "+rq if rq else "",  "get oid error "+rq2 if rq2 else ""}"}
    except Exception as e:
        raise HTTPException(500,f"Error canot insert oil data to database {e}")

### Update items
 
@basicRoutes.patch("/update_oil_info", tags=['Data Entry endpoint'], name="Oil info Update", description="Update user data oil info only specific fields")
async def update_info(id:int,data: CarOilInfoUpdater, token: str = Depends(get_current_user)):
    cuid = token['id']
    if not await user_exist(tokens=token):
        raise HTTPException(404,"Invalid token no such user exist")
   
    uide=await RunQuery(q="""
                          SELECT 1  FROM Oil_Change OC
                          JOIN UserOil UO ON OC.id = UO.oil_id
                          WHERE OC.id =? AND UO.user_id = ?
                          """,
                          val=(id,cuid),
                          sqmq=False,
                          rom=False)
    if not uide:
        raise HTTPException(500,"User not allowed to  update that or entry dont exist!!")
    # Initialize an empty list to store the update query parameters
    update_values = []

    # Initialize the update query with the SET clause
    update_query = "UPDATE Oil_Change SET"

    # Check each field provided in the request and update the query accordingly
    if data.car_name:
        update_query += " car_name = ?,"
        update_values.append(data.car_name)

    if data.car_model is not None:
        update_query += " car_model = ?,"
        update_values.append(data.car_model)

    if data.odometer_reading is not None:
        update_query += " odometer_reading = ?,"
        update_values.append(data.odometer_reading)

    if data.odometer_reading_next is not None:
        update_query += " odometer_reading_next = ?,"
        update_values.append(data.odometer_reading_next)

    if data.oil_change_date:
        update_query += " oil_change_date = ?,"
        update_values.append(data.oil_change_date)

    if data.next_oilChange_date:
        update_query += " next_oilChange_date = ?,"
        update_values.append(data.next_oilChange_date)

    if data.oil_grade:
        update_query += " oil_grade = ?,"
        update_values.append(data.oil_grade)

    if data.provider:
        update_query += " provider = ?,"
        update_values.append(data.provider)

    if data.total_cost is not None:
        update_query += " total_cost = ?,"
        update_values.append(data.total_cost)

    if data.oil_vendor:
        update_query += " oil_vander = ?,"
        update_values.append(data.oil_vendor)
    
    if data.air_filter:
        update_query += " air_filter = ?,"
        update_values.append(data.air_filter)

    if data.oil_filter:
        update_query += " oil_filter = ?,"
        update_values.append(data.oil_filter)

    if data.ac_filter:
        update_query += " ac_filter = ?,"
        update_values.append(data.ac_filter)

    if data.notes:
        update_query += " notes = ?,"
        update_values.append(data.notes)

    # Remove the trailing comma from the update query
    update_query = update_query.rstrip(",")

    # Add the WHERE clause to update the data only for the current user
    update_query += " WHERE id = ? AND id IN (SELECT oid FROM License_Plate WHERE uid = ?)"
    update_values.extend([id, cuid])

    try:
        # Execute the update query
        await RunQuery(update_query, tuple(update_values))

        return {"message": "Oil information updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update oil information: {str(e)}")

##Update licance
@basicRoutes.patch("/update_license_number", tags=['Data Entry endpoint'], name="Update License Number", description="Update the license number associated with oil change information")
async def update_license_number(ld: LicancePlateInfoUpdater, token: str = Depends(get_current_user)):
    cuid = token['id']
    if not await user_exist(tokens=token):
        raise HTTPException(404,"Invalid token no such user exist")
    uide=await RunQuery(q="""
                            SELECT 1
                            FROM License_Plate LP
                            JOIN user u ON LP.uid = u.id
                            WHERE LP.id = ? AND LP.license_number = ?;
                          """,
                          val=(cuid,ld.license_number),
                          sqmq=False,
                          rom=False)
    if not uide:
        raise HTTPException(500,"User not allowed to  update that or entry dont exist!!")
    try:
        # Construct the SQL query to update the license number
        update_query = """
            UPDATE License_Plate 
            SET license_number = ? 
            WHERE id IN (
                SELECT ulp.license_plate_id 
                FROM User_License_Plate ulp 
                INNER JOIN License_Plate lp ON ulp.license_plate_id = lp.id 
                WHERE ulp.user_id = ?)
        """
        # Execute the query
        await RunQuery(update_query, (ld.old_license_number, cuid))

        return {"message": "License number updated successfully"}
    except Exception as e:
        # Handle any exceptions that occur during the query execution
        raise HTTPException(status_code=500, detail=f"Failed to update license number: {str(e)}")



### Get all data of current user
 
@basicRoutes.get("/get_all", tags=['Data Fetch Endpoint'], name='Get all data of car oil', description='all cars data and oil related info of nomatter how many car you have' )
async def get_all(token: str = Depends(get_current_user)):
    try:
        cuid = token['id']
        if not await user_exist(tokens=token):
            raise HTTPException(404,"Invalid token no such user exist")
        all_data = await RunQuery(
            q=f"""
                SELECT 
                    LP.license_number,
                    OC.car_name,
                    OC.car_model,
                    OC.odometer_reading,
                    OC.odometer_reading_next,
                    OC.oil_change_date,
                    OC.next_oilChange_date,
                    OC.oil_grade,
                    OC.provider,
                    air_filter,
                    oil_filter,
                    ac_filter,
                    OC.total_cost,
                    OC.oil_vander,
                    OC.notes,
                    OC.last_update,
                    OC.creation_date
                FROM 
                    Oil_Change OC
                LEFT JOIN 
                    License_Plate LP ON OC.id = LP.oid
                    JOIN OilEntry oe ON license_plate_id=LP.id
                   
                WHERE
                    OC.cuid = ?
            """,
            val=(cuid,),
            rom=True,
            sqmq=False
        )

        rf=[]
     
        for d in all_data:
            rf.append({
                "licance_number":d[0] ,
                "car_name":d[1],
                "model":d[2],
                "odometer_reading":d[3],
                 "odometer_reading_next":d[4],
                   "Oil_change_date":d[5],
                   "next_oilChange_date":d[6],
                   "oil_grade":d[7],
                    "provider":d[8],
                    "air_filter":d[9],
                    "oil_filter":d[10],
                    "ac_filter":d[11],
                    "total_cost":d[12],
                    "oil_vander":d[13],
                    "notes":d[14],
                    "last_update":d[15],
                    "creation_date":d[16]
           
            })
        return rf
    except Exception as e:
        raise HTTPException(500, f"Error retrieving car oil data: {e}")
 
 ## Get  by licance plate
@basicRoutes.get("/get_by_licance", tags=['Car Oil data Get'], name='Get data by license number', description='Search by license plate')
async def get_all(licance: str = Query(..., title="Search by license plate", description="Search oil data by license plate number"), token: str = Depends(get_current_user)):
    try:
        cuid = token['id']
        if not await user_exist(tokens=token):
            raise HTTPException(404,"Invalid token no such user exist")
        all_data = await RunQuery(
            q="""
               SELECT 
                    LP.license_number,
                    OC.car_name,
                    OC.car_model,
                    OC.odometer_reading,
                    OC.odometer_reading_next,
                    OC.oil_change_date,
                    OC.next_oilChange_date,
                    OC.oil_grade,
                    OC.provider,
                    air_filter,
                    oil_filter,
                    ac_filter,
                    OC.total_cost,
                    OC.oil_vander,
                    OC.notes,
                    OC.last_update,
                    OC.creation_date
                FROM 
                    Oil_Change OC
                LEFT JOIN 
                    License_Plate LP ON OC.id = LP.oid
                    JOIN OilEntry oe ON license_plate_id=LP.id
        WHERE
            OC.cuid = ? AND LP.license_number = ?
            """,
            val=(cuid, licance),
            rom=True,
            sqmq=False
        )

        response_data = []
        for d in all_data:
            response_data.append({
                "licance_number": d[0],
                "car_name": d[1],
                "model": d[2],
                "odometer_reading": d[3],
                "odometer_reading_next": d[4],
                "Oil_change_date": d[5],
                "next_oilChange_date": d[6],
                "oil_grade": d[7],
                "provider": d[8],
                "air_filter":d[9],
                "oil_filter":d[10],
                "ac_filter":d[11],
                "total_cost":d[12],
                "oil_vander":d[13],
                "notes":d[14],
                "last_update":d[15],
                 "creation_date":d[16]
            })

        return response_data
    except Exception as e:
        raise HTTPException(500, f"Error retrieving car oil data: {e}")
    
### Get LICENCE number for current user

@basicRoutes.get('/get_license_number', tags=['Data Fetch Endpoint'])
async def get_licence(token: str = Depends(get_current_user)):
    try:
        cuid = token['id']
        dd = []
        if not await user_exist(tokens=token):
            raise HTTPException(404,"Invalid token no such user exist")
        # Ensure that the parameter is passed as a tuple, even if it contains only one value
        licno = await RunQuery(
            q="""SELECT LP.id, LP.license_number
                 FROM License_Plate LP 
                 JOIN User_License_Plate ulp ON LP.id = ulp.license_plate_id
                 JOIN User u ON ulp.user_id = u.id
                 WHERE u.id = ?
                 """,
            val=(cuid,),  # Note the comma to create a tuple with one element
            sqmq=False,
            rom=True
        )
        
        # Check if no records found
        if licno is None:
            return Response(content="No records found", status_code=404)
        
        # Format the data into a list of dictionaries
        dd = [{"id": data[0], "license_no": data[1]} for data in licno]
        
        return dd
    except Exception as e:
        raise HTTPException(500, f"Error occurred while fetching license plate: {e}")


### Alert of oil change date when dates are same

@basicRoutes.get(path="/get_alert", tags=['Data Fetch Endpoint'], name="Get alert for oil change")
async def get_alert(token: str = Depends(get_current_user)):
    try:
        rd = []
        uid = token['id']
        if not await user_exist(tokens=token):
            raise HTTPException(404,"Invalid token no such user exist")
        current_date = datetime.now().strftime("%d-%m-%y")
        print(current_date, type(current_date))
        ddata = await RunQuery(
            q="""SELECT 
                    OC.car_name,
                    OC.oil_change_date,
                    OC.next_oilChange_date
                FROM 
                    Oil_Change OC
                WHERE 
                    OC.next_oilChange_date = ?
                    AND OC.cuid = ?""",
            val=(current_date, uid),
            sqmq=False,
            rom=True
        )

        for d in ddata:
            rd.append({"car_name": d[0], "current_date": d[1], "next_date": d[2]})

        if rd:
            return rd
        else:
            return {"message": "No oil change alerts found for today."}

    except Exception as e:
        raise HTTPException(500, f"Failed to retrieve data for oil change alerts: {e}")

## Delete specific record

@basicRoutes.delete("/delete_record", tags=['Data Dangerzone Endpoint'], name="Delete a specific record")
async def delete_record(oil_id: int, token: str = Depends(get_current_user)):
    try:
        uid = token['id']
        
        # Check if the user exists
        if not await user_exist(tokens=token):
            raise HTTPException(404, "User doesn't exist or is using an invalid token")
        
        # Check if the provided oil_id exists for the current user
        check_query = """
                      SELECT 1  FROM Oil_Change OC
                      JOIN UserOil UO ON OC.id = UO.oil_id
                      WHERE OC.id = ? AND UO.user_id = ?
                      """
        check_result = await RunQuery(q=check_query, val=(oil_id, uid), rom=False, sqmq=False)
        if not check_result:
            raise HTTPException(404, "The specified record doesn't exist or you don't have permission to delete it")
        goid = await RunQuery(q="""
                            SELECT OC.id FROM Oil_Change OC
                            JOIN UserOil UO ON OC.id = UO.oil_id
                            WHERE OC.id = ? AND UO.user_id = ?
                            """, val=(oil_id, uid), sqmq=False, rom=False)

        # Delete the record from the Oil_Change table
        delete_query = "DELETE FROM Oil_Change WHERE id = ?"
        await RunQuery(q=delete_query, val=(oil_id,), rom=False, sqmq=False)
        doe=await RunQuery(q="""
                             DELETE FROM OilEntry WHERE oil_id=?
                             """,
                             rom=False,
                             sqmq=False,
                             val=(goid[0],))
        duo=await RunQuery(q="""
                             DELETE FROM UserOil WHERE oil_id=?
                             """,
                             rom=False,
                             sqmq=False,
                             val=(goid[0],))
        return {"message": "Record deleted successfully"}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(500, f"Error occurred while deleting record: {e}")
 

### Check user exist21

@basicRoutes.get(path='/user_exist',tags=['Debug'])
async def user_exists(token:str=Depends(get_current_user)):
    try:
        data=await user_exist(tokens=token)
        
        if data:
            return True
        else:
            return False
    except Exception as e:
        raise HTTPException(500,f"Error get data for user existance due to {e}")
    

