import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException
import os
from dotenv import load_dotenv
load_dotenv()

ip = os.getenv("IP")
db_name = os.getenv("DB_NAME")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

connection = None  # Define connection variable outside try block

try:
    # Establish the connection
    connection = mysql.connector.connect(
        host=ip,
        database=db_name,
        user=username,
        password=password
    )
    
    if connection.is_connected():
        print("Successfully connected to the database")
        # Get database information
        db_info = connection.get_server_info()
        print("Server version:", db_info)
        
        # Create a cursor object
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print("Connected to database:", record)
        
        # Perform any additional database operations here
        
        # Close the cursor (Do not close the connection here, it should be closed outside the try block)
        cursor.close()
        print("MySQL cursor is closed")

except Error as e:
    print("Error while connecting to MySQL", e)
   

async def RunQuery(q: str, val: tuple = (), sqmq=False, rom=False) -> tuple:
    try:
        # Creating a cursor object from the existing connection
        cursor = connection.cursor()
        
        # Executing the query
        if not sqmq:
            cursor.execute(q, val)
        else:
            cursor.executemany(q, val)
        
        # Fetching results if needed
        if not rom:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        
        # Closing cursor
        cursor.close()
        
        return result
    
    except Exception as e:
        print("Error running SQL query:", e)
        raise e