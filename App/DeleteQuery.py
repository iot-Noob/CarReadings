from config.connectDb import *

queries=[
"""
DELETE FROM Oil_Change
WHERE id IN (
SELECT Oil_Change.id
FROM Oil_Change
JOIN OilEntry ON Oil_Change.id = OilEntry.oil_id
JOIN License_Plate ON OilEntry.license_plate_id = License_Plate.id
JOIN User_License_Plate ON License_Plate.id = User_License_Plate.license_plate_id
JOIN User ON User_License_Plate.user_id = User.id
WHERE   User.id =? AND License_Plate.license_number = ?
); 
""",

"""
DELETE FROM OilEntry
WHERE license_plate_id IN (
SELECT lp.id
FROM License_Plate lp
JOIN User_License_Plate ulp ON lp.id = ulp.license_plate_id
WHERE ulp.user_id = ? AND lp.license_number = ?
);
""",

"""
DELETE FROM UserOil
WHERE oil_id IN (
SELECT oc.id
FROM Oil_Change oc
FULL JOIN License_Plate lp ON oc.cuid = lp.uid
WHERE lp.uid =? AND lp.license_number =?
);
""",

"""
DELETE FROM User_License_Plate
WHERE license_plate_id IN (
SELECT lp.id
FROM License_Plate lp
WHERE lp.uid = ?  AND lp.license_number = ?
);
""",

"""
DELETE FROM Oil_Change
WHERE cuid = ? AND id IN (
    SELECT oc.id
    FROM Oil_Change oc
    JOIN License_Plate lp ON oc.cuid = lp.uid
    WHERE lp.uid = ? AND lp.license_number = ?
);
""",

"""
DELETE FROM License_Plate
WHERE uid =? AND license_number =?;
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