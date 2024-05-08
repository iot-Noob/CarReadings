import aiosqlite
from dotenv import load_dotenv
import os
from fastapi import HTTPException
load_dotenv()

try: 
    db_path = os.getenv("DP_PATH")
    print("DB Connection success!!")
except Exception as e:
    print("Error connect to DB ", e)
 
async def RunQuery(q: str, val: tuple = (), sqmq=False, rom=False) -> tuple:
    try:
        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.cursor()
            if not sqmq:
                await cursor.execute(q, val)
            else:
                await cursor.executemany(q, val)
            await conn.commit()
            if not rom:
                return await cursor.fetchone()
            else:
                return await cursor.fetchall()
    except Exception as e:
        print("Error running SQL query:", e)
        raise HTTPException(status_code=500, detail=f"Failed to execute query: {str(e)}")


 
 
