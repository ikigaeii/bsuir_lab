from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


async def create_client(db: AsyncIOMotorDatabase, client_data: dict) -> dict:
    """
    Creates a new client in the database.
    """
    result = await db["clients"].insert_one(client_data)
    client = await db["clients"].find_one({"_id": result.inserted_id})
    return client


async def get_client_by_id(db: AsyncIOMotorDatabase, client_id: str) -> dict | None:
    """
    Retrieves a client by its ID.
    """
    if not ObjectId.is_valid(client_id):
        return None
    client = await db["clients"].find_one({"_id": ObjectId(client_id)})
    return client if client else None


async def get_all_clients(
    db: AsyncIOMotorDatabase, limit: int = 100, skip: int = 0
) -> list[dict]:
    """
    Retrieves a list of all clients, with optional pagination.
    """
    cursor = db["clients"].find().skip(skip).limit(limit)
    clients = await cursor.to_list(length=limit)
    return clients


async def update_client(db: AsyncIOMotorDatabase, client_id: str, updated_data: dict) -> bool:
    """
    Updates a client by its ID.
    """
    if not ObjectId.is_valid(client_id):
        return False
    result = await db["clients"].update_one(
        {"_id": ObjectId(client_id)}, {"$set": updated_data}
    )
    return result.modified_count > 0


async def delete_client(db: AsyncIOMotorDatabase, client_id: str) -> bool:
    """
    Deletes a client by its ID.
    """
    if not ObjectId.is_valid(client_id):
        return False
    result = await db["clients"].delete_one({"_id": ObjectId(client_id)})
    return result.deleted_count > 0
