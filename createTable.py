from connectDb import RunQuery

async def UserTable():
    try:
            await RunQuery(q="""
                        CREATE TABLE IF NOT EXISTS user (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        username VARCHAR(133) UNIQUE,
                        password VARCHAR(122),
                        is_online BOOLEAN,
                        email VARCHAR UNIQUE,
                        disable BOOLEAN,
                        pic VARCHAR(200),
                        creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_update  DEFAULT CURRENT_TIMESTAMP,
                        lpid INTEGER   UNIQUE,
                        FOREIGN KEY (lpid) REFERENCES License_Plate(uid))
                        """, val=(),sqmq=False,rom=False)
    except Exception as e:
        print("Error creating user table: ", e)

async def OilDateTable():
    try:
            await RunQuery(q="""
                        CREATE TABLE IF NOT EXISTS Oil_Change (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        car_name VARCHAR (244) NOT NULL,
                        car_model INTEGER,
                        odometer_reading INTEGER NOT NULL,
                        odometer_reading_next INTEGER NOT NULL,
                        oil_change_date DATETIME,
                        next_oilChange_date DATETIME,
                        oil_grade VARCHAR (100),
                        provider VARCHAR (100),
                        total_cost INTEGER,
                        oil_vander VARCHAR (200),
                        notes TEXT,
                        creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_update  DEFAULT CURRENT_TIMESTAMP,
                        cuid INTEGER, 
                        FOREIGN KEY (cuid) REFERENCES user(id)
                        )
                        """, val=(),sqmq=False,rom=False)
    except Exception as e:
        print("Error creating user table: ", e)


async def Licance_Plate():
    try:
            await RunQuery(q="""
                        CREATE TABLE IF NOT EXISTS License_Plate (
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            license_number VARCHAR(30),
                            uid INTEGER   NOT NULL,
                            oid INTEGER NOT NULL,
                            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_update  DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (uid) REFERENCES User(id),
                            FOREIGN KEY (oid) REFERENCES Oil_Change(id)
                        ) 

                        """, val=(),sqmq=False,rom=False)
    except Exception as e:
        print("Error creating user table: ", e)