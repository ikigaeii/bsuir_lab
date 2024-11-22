from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

MONGODB_URI = "mongodb://127.0.0.1:27017"
DATABASE_NAME = "airport"


@app.on_event("startup")
async def startup_db():
    app.state.mongodb_client = AsyncIOMotorClient(MONGODB_URI)
    app.state.db = app.state.mongodb_client[DATABASE_NAME]


@app.on_event("shutdown")
async def shutdown_db():
    app.state.mongodb_client.close()


from src.app.api.flight import router as flight_router
from src.app.api.passport import router as passport_router
from src.app.api.client import router as client_router
from src.app.api.reservation import router as reservation_router

app.include_router(flight_router, prefix="/api/v1/flights", tags=["Flights"])
app.include_router(passport_router, prefix="/api/v1/passports", tags=["Passports"])
app.include_router(client_router, prefix="/api/v1/clients", tags=["Clients"])
app.include_router(reservation_router, prefix="/api/v1/reservations", tags=["Reservations"])



@app.get("/")
async def root():
    return {"message": "Welcome to the Flight API"}
