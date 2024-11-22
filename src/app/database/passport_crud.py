from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


async def create_passport(db: AsyncIOMotorDatabase, passport_data: dict) -> dict:
    """
    Creates a new passport in the database.
    """
    result = await db["passports"].insert_one(passport_data)
    passport = await db["passports"].find_one({"_id": result.inserted_id})
    return passport


async def get_passport_by_id(db: AsyncIOMotorDatabase, passport_id: str) -> dict | None:
    """
    Retrieves a passport by its ID.
    """
    if not ObjectId.is_valid(passport_id):
        return None
    passport = await db["passports"].find_one({"_id": ObjectId(passport_id)})
    return passport if passport else None


async def get_all_passports(
    db: AsyncIOMotorDatabase, limit: int = 100, skip: int = 0
) -> list[dict]:
    """
    Retrieves a list of all passports, with optional pagination.
    """
    cursor = db["passports"].find().skip(skip).limit(limit)
    passports = await cursor.to_list(length=limit)
    return passports


async def update_passport(db: AsyncIOMotorDatabase, passport_id: str, updated_data: dict) -> bool:
    """
    Updates a passport by its ID.
    """
    if not ObjectId.is_valid(passport_id):
        return False
    result = await db["passports"].update_one(
        {"_id": ObjectId(passport_id)}, {"$set": updated_data}
    )
    return result.modified_count > 0


async def delete_passport(db: AsyncIOMotorDatabase, passport_id: str) -> bool:
    """
    Deletes a passport by its ID.
    """
    if not ObjectId.is_valid(passport_id):
        return False
    result = await db["passports"].delete_one({"_id": ObjectId(passport_id)})
    return result.deleted_count > 0
