from config.connectDb import *
#from config.MysqlConnector import RunQuery ##MYSQL Server via sql.connector

async def dinfo(info:str,index:int):
    dinfo=[
    f"Delete UserOil table {info if info else ""}",
    f"Delete User_License_Plate table {info if info else ""}",
    f"Delete Oil_Change table {info if info else ""}",
    f"Delete OilEntry table {info if info else ""}",
    f"Delete License_Plate table {info if info else ""}", 
          ]
    return dinfo[index]
queries=[
"""
DELETE FROM UserOil
WHERE oil_id IN (
    SELECT oe.oil_id
    FROM OilEntry oe
    INNER JOIN License_Plate lp ON oe.license_plate_id = lp.id
    WHERE lp.license_number = ?
);
""",

"""
DELETE FROM User_License_Plate
WHERE license_plate_id IN (
    SELECT lp.id
    FROM License_Plate lp
    INNER JOIN OilEntry oe ON lp.id = oe.license_plate_id
    WHERE lp.license_number = ?
);
""",

"""
 DELETE FROM Oil_Change 
WHERE id IN (
    SELECT oc.id
    FROM OilEntry
    INNER JOIN Oil_Change oc ON OilEntry.oil_id = oc.id
    INNER JOIN License_Plate lp ON OilEntry.license_plate_id = lp.id
    WHERE lp.license_number =?
);
""",

"""
DELETE FROM OilEntry 
WHERE id IN (
    SELECT oe.id 
    FROM OilEntry oe 
    LEFT JOIN License_Plate lp ON oe.license_plate_id = lp.id 
    WHERE lp.license_number =?
);
""",

"""
DELETE FROM License_Plate 
WHERE uid = ?
  AND license_number = ?;
""" 

]

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
    
async def DrpoTables(): ### Super hot query 
    try:
        dq=[
            """DROP TABLE IF EXISTS UserOil;
            """,
            """
            DROP TABLE IF EXISTS OilEntry;
            """,
            """
            DROP TABLE IF EXISTS User_License_Plate;
            """,
            """
             DROP TABLE IF EXISTS Oil_Change;

            """,
            """
            DROP TABLE IF EXISTS License_Plate;
            """
            
        ]

        for ind,d in enumerate(dq):
            try:
                await RunQuery(q=d,val=(),sqmq=False,rom=False)
            except Exception as e:
                raise HTTPException(500,f"Canr delete table at index query {ind} due to {e}")
    except Exception as e:
        raise HTTPException(500,f"Unable ot drop table due to {e}")