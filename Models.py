from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    is_online:bool|None=None

class Token(BaseModel):
    access_token: str
    token_type: str
    