from fastapi import FastAPI
from routes.properti import properti_router, kenaikan_router
from routes.auth import auth_router

app = FastAPI()

app.include_router(properti_router, prefix="/properti")
app.include_router(kenaikan_router, prefix="/kenaikan")
app.include_router(auth_router)