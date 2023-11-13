from pydantic import BaseModel 
from uuid import UUID

class UserIn(BaseModel): 
    username : str 
    password : str 

    class config:
        json_schema_extra = {
            "example" : {
                "username" : "ain", 
                "password" : "ainain"
            }
        }

class Token(BaseModel): 
    access_token : str 
    token_type : str = "bearer"

class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None

class UserOut(BaseModel):
    id: UUID
    email: str

class SystemUser(UserOut):
    password: str