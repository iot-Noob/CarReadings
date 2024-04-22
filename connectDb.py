import sqlite3
from dotenv import load_dotenv
import os
from functools import lru_cache
load_dotenv()

try: 
    db_path= os.getenv("DP_PATH")
    print("DB Connection sucess!!")
    conn=sqlite3.connect(db_path)
except Exception as e:
    print("Error connect to DB ",e)


cursor=conn.cursor()

@lru_cache(maxsize=256)
def RunQuery(q:str,val:tuple,sqmq=False,rom=False)->tuple:
    try:
        if not sqmq:
            cursor.execute(q,val)
        else:
            cursor.executemany(q,val)
        if not rom:
            return cursor.fetchone
        else:
            return cursor.fetchall
        conn.close()
    except Exception as e:
        print("Error run Swql query ",e)