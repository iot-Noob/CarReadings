from config.connectDb import RunQuery

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
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """, val=(), sqmq=False, rom=False)
    except Exception as e:
        print("Error creating user table: ", e)

async def OilDateTable():
    try:
            await RunQuery(q="""
                            CREATE TABLE IF NOT EXISTS Oil_Change (
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            car_name VARCHAR (244) NOT NULL,
                            car_model INTEGER NOT NULL,
                            odometer_reading INTEGER NOT NULL,
                            odometer_reading_next INTEGER NOT NULL,
                            oil_change_date  DATETIME NOT NULL,
                            next_oilChange_date  DATETIME  ,
                            oil_grade VARCHAR (100) NOT NULL,   
                            provider VARCHAR (100) NOT NULL,
                            air_filter VARCHAR(255),
                            oil_filter VARCHAR(255),
                            ac_filter VARCHAR(255),    
                            total_cost INTEGER NOT NULL,
                            oil_vander VARCHAR (200) NOT NULL,
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
                            license_number VARCHAR(30)   NOT NULL UNIQUE,
                            uid INTEGER   NOT NULL,
                            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_update  DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (uid) REFERENCES User(id)
                           
                        );

                        """, val=(),sqmq=False,rom=False)
    except Exception as e:
        print("Error creating user table: ", e)

async def User_License_Plate():
    try:
        await RunQuery(q="""
            CREATE TABLE IF NOT EXISTS User_License_Plate (
                
                user_id INTEGER,
                license_plate_id INTEGER, 
                FOREIGN KEY (user_id) REFERENCES User(id),
                FOREIGN KEY (license_plate_id) REFERENCES License_Plate(id) 
            );
        """)
    except Exception as e:
        print("Failed to create User_License_Plate table: ", e)
 
async def UserOilEntry(): ## For same oil entry on same licence plate
    try:
        await RunQuery(q="""
                CREATE TABLE IF NOT EXISTS OilEntry (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                license_plate_id INTEGER, 
                oil_id INTEGER, 
                FOREIGN KEY (license_plate_id) REFERENCES License_Plate(id), 
                FOREIGN KEY (oil_id) REFERENCES Oil_Change(id) 
            )
        """)
    except Exception as e:
        print("Failed to create User OilEntry due to :::  ", e)

async def OilUserRelation():
     try:
          await RunQuery(q="""
                              CREATE TABLE IF NOT EXISTS UserOil (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                oil_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (oil_id) REFERENCES Oil_Change(id),
                FOREIGN KEY (user_id) REFERENCES user(id)
                           )
                            
                           """,
                            val=(),
                            sqmq=False,
                            rom=False)
          pass
     except Exception as e:
          print("Error occur creating oil user table due to ",e)