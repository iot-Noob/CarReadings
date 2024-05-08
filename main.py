from fastapi import *
from fastapi.security import *
from fastapi.requests import *
from fastapi.responses import *
from fastapi.middleware.cors import CORSMiddleware
from routes.routes import  basicRoutes


app = FastAPI(title="Car Oil Readings API")
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
   
]

 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
app.include_router(basicRoutes)