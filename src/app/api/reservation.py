from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.app.schemas.shema import ReservationCreate, ReservationResponse, ReservationFull
from src.app.database.database import get_db
from src.app.database.reservation_crud import create_reservation, get_reservation_by_id, get_all_reservations, update_reservation, delete_reservation

router = APIRouter()


@router.post("/", response_model=ReservationResponse, status_code=201)
async def create_new_reservation(reservation: ReservationCreate, db=Depends(get_db)):
    """
    Create a new reservation.
    """
    return await create_reservation(db, reservation.dict())


@router.get("/{reservation_id}", response_model=ReservationFull)
async def get_reservation(reservation_id: str, db=Depends(get_db)):
    """
    Retrieve a reservation by ID.
    """
    return await get_reservation_by_id(db, reservation_id)


@router.get("/", response_model=List[ReservationResponse])
async def list_reservations(skip: int = 0, limit: int = 10, db=Depends(get_db)):
    """
    List all reservations with pagination.
    """
    return await get_all_reservations(db, limit, skip)


@router.put("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation_data(reservation_id: str, reservation: ReservationCreate, db=Depends(get_db)):
    """
    Update an existing reservation by ID.
    """
    return await update_reservation(db, reservation_id, reservation.dict())


@router.delete("/{reservation_id}", response_model=ReservationResponse)
async def delete_existing_reservation(reservation_id: str, db=Depends(get_db)):
    """
    Delete a reservation by ID.
    """
    return await delete_reservation(db, reservation_id)
