from bson import ObjectId
from pymongo.database import Database
from fastapi import HTTPException
from typing import List, Optional


async def create_reservation(db: Database, reservation_data: dict) -> dict:
    """
    Create a new reservation in the database.
    """
    try:
        result = await db["reservations"].insert_one(reservation_data)
        reservation = await db["reservations"].find_one({"_id": result.inserted_id})
        if reservation:
            reservation["id"] = str(reservation.pop("_id"))
        return reservation
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating reservation: {str(e)}")


async def get_reservation_by_id(db: Database, reservation_id: str) -> dict:
    """
    Retrieve a reservation by its ID.
    """
    try:
        object_id = ObjectId(reservation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid reservation ID format")

    reservation = await db["reservations"].find_one({"_id": object_id})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation["id"] = str(reservation.pop("_id"))
    return reservation


async def get_all_reservations(db: Database, limit: int = 10, skip: int = 0) -> List[dict]:
    """
    Retrieve all reservations with pagination.
    """
    reservations = await db["reservations"].find().skip(skip).limit(limit).to_list(length=limit)
    for reservation in reservations:
        reservation["id"] = str(reservation.pop("_id"))
    return reservations


async def update_reservation(db: Database, reservation_id: str, update_data: dict) -> dict:
    """
    Update a reservation by its ID.
    """
    try:
        object_id = ObjectId(reservation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid reservation ID format")

    result = await db["reservations"].update_one({"_id": object_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Reservation not found or no changes made")

    updated_reservation = await db["reservations"].find_one({"_id": object_id})
    updated_reservation["id"] = str(updated_reservation.pop("_id"))
    return updated_reservation


async def delete_reservation(db: Database, reservation_id: str) -> dict:
    """
    Delete a reservation by its ID.
    """
    try:
        object_id = ObjectId(reservation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid reservation ID format")

    reservation = await db["reservations"].find_one({"_id": object_id})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    await db["reservations"].delete_one({"_id": object_id})
    reservation["id"] = str(reservation.pop("_id"))
    return reservation
