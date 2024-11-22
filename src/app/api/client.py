from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from src.app.database.database import get_db
from src.app.schemas.shema import ClientCreate, ClientResponse, ClientBase

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/", response_model=ClientResponse, status_code=201)
async def create_client(client: ClientCreate, db=Depends(get_db)):
    """
    Create a new client.
    """
    try:
        passport = await db.passports.find_one({"_id": ObjectId(client.passport_id)})
        if not passport:
            raise HTTPException(status_code=404, detail="Passport not found")

        client_data = client.model_dump()
        client_data["passport_id"] = client.passport_id

        new_client = await db.clients.insert_one(client_data)
        created_client = await db.clients.find_one({"_id": new_client.inserted_id})

        if created_client:
            created_client["id"] = str(created_client.pop("_id"))
        return jsonable_encoder(created_client)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str, db=Depends(get_db)):
    """
    Retrieve a client by ID.
    """
    try:
        object_id = ObjectId(client_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid client ID format")

    client = await db.clients.find_one({"_id": object_id})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client["id"] = str(client.pop("_id"))
    return client


@router.get("/", response_model=List[ClientResponse])
async def list_clients(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
        db=Depends(get_db)
):
    """
    Retrieve a list of clients with pagination.
    """
    clients = await db.clients.find().skip(skip).limit(limit).to_list(limit)

    for client in clients:
        client["id"] = str(client.pop("_id"))
    return clients


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
        client_id: str,
        client_update: ClientBase,
        db=Depends(get_db)
):
    """
    Update client details by ID.
    """
    try:
        object_id = ObjectId(client_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid client ID format")

    update_data = {
        k: v for k, v in client_update.model_dump().items() if v is not None
    }

    if update_data:
        result = await db.clients.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Client not found")

        updated_client = await db.clients.find_one({"_id": object_id})
        updated_client["id"] = str(updated_client.pop("_id"))
        return updated_client
    return await get_client(client_id, db)


@router.delete("/{client_id}", status_code=204)
async def delete_client(client_id: str, db=Depends(get_db)):
    """
    Delete a client by ID.
    """
    try:
        object_id = ObjectId(client_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid client ID format")

    result = await db.clients.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")


@router.get("/search", response_model=List[ClientResponse])
async def search_clients(
        mail: str = Query(default=None),
        phone_number: str = Query(default=None),
        nick_name: str = Query(default=None),
        db=Depends(get_db)
):
    """
    Search clients by email, phone number, or nickname.
    """
    query = {}
    if mail:
        query["mail"] = mail
    if phone_number:
        query["phone_number"] = phone_number
    if nick_name:
        query["nick_name"] = nick_name

    clients = await db.clients.find(query).to_list(None)

    for client in clients:
        client["id"] = str(client.pop("_id"))
    return clients
