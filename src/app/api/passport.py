from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from src.app.database.database import get_db
from src.app.schemas.shema import PassportCreate, PassportResponse, PassportBase

router = APIRouter(prefix="/passports", tags=["passports"])


@router.post("/", response_model=PassportResponse, status_code=201)
async def create_passport(passport: PassportCreate, db=Depends(get_db)):
    """
    Create a new passport.
    """
    try:
        new_passport = await db.passports.insert_one(passport.model_dump())
        created_passport = await db.passports.find_one({"_id": new_passport.inserted_id})

        if created_passport:
            created_passport["id"] = str(created_passport.pop("_id"))
        return jsonable_encoder(created_passport)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{passport_id}", response_model=PassportResponse)
async def get_passport(passport_id: str, db=Depends(get_db)):
    """
    Retrieve a passport by ID.
    """
    try:
        object_id = ObjectId(passport_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid passport ID format")

    passport = await db.passports.find_one({"_id": object_id})
    if not passport:
        raise HTTPException(status_code=404, detail="Passport not found")

    passport["id"] = str(passport.pop("_id"))
    return passport


@router.get("/", response_model=List[PassportResponse])
async def list_passports(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
        db=Depends(get_db)
):
    """
    Retrieve a list of passports with pagination.
    """
    passports = await db.passports.find().skip(skip).limit(limit).to_list(limit)

    for passport in passports:
        passport["id"] = str(passport.pop("_id"))
    return passports


@router.put("/{passport_id}", response_model=PassportResponse)
async def update_passport(
        passport_id: str,
        passport_update: PassportBase,
        db=Depends(get_db)
):
    """
    Update passport details by ID.
    """
    try:
        object_id = ObjectId(passport_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid passport ID format")

    update_data = {
        k: v for k, v in passport_update.model_dump().items() if v is not None
    }

    if update_data:
        result = await db.passports.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Passport not found")

        updated_passport = await db.passports.find_one({"_id": object_id})
        updated_passport["id"] = str(updated_passport.pop("_id"))
        return updated_passport
    return await get_passport(passport_id, db)


@router.delete("/{passport_id}", status_code=204)
async def delete_passport(passport_id: str, db=Depends(get_db)):
    """
    Delete a passport by ID.
    """
    try:
        object_id = ObjectId(passport_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid passport ID format")

    result = await db.passports.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Passport not found")


@router.get("/search", response_model=List[PassportResponse])
async def search_passports(
        passport_number: str = Query(default=None),
        firstname: str = Query(default=None),
        lastname: str = Query(default=None),
        db=Depends(get_db)
):
    """
    Search passports by passport number, firstname, or lastname.
    """
    query = {}
    if passport_number:
        query["passport_number"] = passport_number
    if firstname:
        query["firstname"] = firstname
    if lastname:
        query["lastname"] = lastname

    passports = await db.passports.find(query).to_list(None)

    for passport in passports:
        passport["id"] = str(passport.pop("_id"))
    return passports
