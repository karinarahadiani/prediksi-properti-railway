from fastapi import APIRouter, FastAPI, status, Depends, HTTPException
from typing import Annotated, Any, Union
from db import cursor, conn
from datetime import timedelta, datetime
import os
from jose import jwt, JWTError
from passlib.context import CryptContext
from models.users import UserIn, UserOut, SystemUser, Token, TokenPayload
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import ValidationError

authRouter = APIRouter(
    tags=["auth"]
)

ALGORITHM = 'HS256'
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
# JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth_bearer = OAuth2PasswordBearer(tokenUrl='/login', scheme_name="JWT")


# buat token
def createAccessToken(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    enc = {"exp": expires_delta, "sub": str(subject)}
    encode_jwt = jwt.encode(enc, JWT_SECRET_KEY, ALGORITHM)
    return encode_jwt

# cek validasi
async def get_current_user(token: str = Depends(oauth_bearer)) -> SystemUser:
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = token_data.sub
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
    
    return username



@authRouter.post("/signup")
async def createNewUser(data: UserIn):
    query = "SELECT username FROM users WHERE username=%s;"
    cursor.execute(query, (data.username,))
    user = cursor.fetchone()

    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username already exist")
    
    hashed_pass = bcrypt_context.hash(data.password)

    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    cursor.execute(query, (data.username, data.password,))
    conn.commit()

    return {
        "success": True,
        "message": f"User dengan username {data.username} berhasil dibuat",
        "code": 200
    }

    

@authRouter.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    query = "SELECT * FROM users WHERE username=%s;"
    cursor.execute(query, (form_data.username,))
    user = cursor.fetchone()

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    
    hashed_pass = user[3] #password
    if not bcrypt_context.verify(form_data.password, hashed_pass):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    
    return {
        "access_token": createAccessToken(user[2]),
        "token_type": "bearer"
    }



# cek dependensi ke login
@authRouter.get("/MyInfo")
async def getMyInfo(user: UserIn = Depends(get_current_user)):
    query = "SELECT username FROM users WHERE username=%s;"
    cursor.execute(query, (user.username,))
    info = cursor.fetchone()
    return {
        "success": True,
        "code": 200,
        "Info": info
    }