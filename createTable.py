from connectDb import *

def UserTable():
    try:
            RunQuery(q="""
                        CREATE TABLE IF NOT EXISTS user (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        username VARCHAR(133),
                        password VARCHAR(122),
                        is_online BOOLEAN,
                        email VARCHAR,
                        disable BOOLEAN,
                        pic VARCHAR(200),
                        creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        lpid INTEGER NOT NULL UNIQUE,
                        FOREIGN KEY (lpid) REFERENCES License_Plate(uid))
                        """, val=())
    except Exception as e:
        print("Error creating user table: ", e)

def OilDateTable():
    try:
            RunQuery(q="""
                        CREATE TABLE IF NOT EXISTS Oil_Change (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        car_name VARCHAR (244) NOT NULL,
                        odometer_reading INTEGER NOT NULL,
                        odometer_reading_next INTEGER NOT NULL,
                        oil_change_date DATETIME,
                        next_oilChange_date DATETIME,
                        oil_grade VARCHAR (100),
                        provider VARCHAR (100),
                        total_cost INTEGER,
                        oil_vander VARCHAR (200),
                        notes TEXT
                        )
                        """, val=())
    except Exception as e:
        print("Error creating user table: ", e)


def Licance_Plate():
    try:
            RunQuery(q="""
                        CREATE TABLE IF NOT EXISTS License_Plate (
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            license_number VARCHAR(30),
                            uid INTEGER UNIQUE NOT NULL,
                            oid INTEGER NOT NULL,
                            FOREIGN KEY (uid) REFERENCES User(id),
                            FOREIGN KEY (oid) REFERENCES Oil_Change(id)
                        ) 

                        """, val=())
    except Exception as e:
        print("Error creating user table: ", e)