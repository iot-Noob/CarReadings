from fastapi import *
from fastapi.security import *
from fastapi.requests import *
from fastapi.responses import *
from createTable import *
from Models import User,Token

bsicRoutes = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
 

@bsicRoutes.on_event('startup')
async def startup_event():\

    print("API IS Starting....")
    UserTable()
    OilDateTable()
    Licance_Plate()        