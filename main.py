from fastapi import FastAPI
from routes.properti import properti_router, kenaikan_router
from routes.auth import authRouter
from tortoise import Tortoise

app = FastAPI()

# Include routers in the app
app.include_router(properti_router)
app.include_router(kenaikan_router)
app.include_router(authRouter)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)
