from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


async def create_flight(db: AsyncIOMotorDatabase, flight_data: dict) -> dict:
    result = await db["flights"].insert_one(flight_data)
    flight = await db["flights"].find_one({"_id": result.inserted_id})
    return flight


async def get_flight_by_id(db: AsyncIOMotorDatabase, flight_id: str) -> dict | None:
    if not ObjectId.is_valid(flight_id):
        return None
    flight = await db["flights"].find_one({"_id": ObjectId(flight_id)})
    return flight if flight else None


async def get_all_flights(db: AsyncIOMotorDatabase, limit: int = 100, skip: int = 0) -> list[dict]:
    cursor = db["flights"].find().skip(skip).limit(limit)
    flights = await cursor.to_list(length=limit)
    return flights


async def update_flight(db: AsyncIOMotorDatabase, flight_id: str, updated_data: dict) -> bool:
    if not ObjectId.is_valid(flight_id):
        return False
    result = await db["flights"].update_one({"_id": ObjectId(flight_id)}, {"$set": updated_data})
    return result.modified_count > 0


async def delete_flight(db: AsyncIOMotorDatabase, flight_id: str) -> bool:
    if not ObjectId.is_valid(flight_id):
        return False
    result = await db["flights"].delete_one({"_id": ObjectId(flight_id)})
    return result.deleted_count > 0
