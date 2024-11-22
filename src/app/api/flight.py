from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from datetime import datetime
from bson import ObjectId

from fastapi.encoders import jsonable_encoder

from src.app.database.database import get_db
from src.app.schemas.shema import FlightCreate, FlightResponse, FlightUpdate

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("/", response_model=FlightResponse, status_code=201)
async def create_flight(flight: FlightCreate, db=Depends(get_db)):
    try:
        datetime.strptime(flight.date_of_flight, "%Y-%m-%d")
        datetime.strptime(flight.departure_time, "%H:%M")

        new_flight = await db.flights.insert_one(flight.model_dump())

        created_flight = await db.flights.find_one({"_id": new_flight.inserted_id})

        if created_flight:
            created_flight["id"] = str(created_flight.pop("_id"))

        return jsonable_encoder(created_flight)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{flight_id}", response_model=FlightResponse)
async def get_flight(flight_id: str, db=Depends(get_db)):
    try:
        object_id = ObjectId(flight_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid flight ID format")

    flight = await db.flights.find_one({"_id": object_id})
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    flight["id"] = str(flight.pop("_id"))
    return flight


@router.get("/", response_model=List[FlightResponse])
async def list_flights(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
        db=Depends(get_db)
):
    flights = await db.flights.find().skip(skip).limit(limit).to_list(limit)

    for flight in flights:
        flight["id"] = str(flight.pop("_id"))
    return flights


@router.put("/{flight_id}", response_model=FlightResponse)
async def update_flight(
        flight_id: str,
        flight_update: FlightUpdate,
        db=Depends(get_db)
):
    try:
        object_id = ObjectId(flight_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid flight ID format")

    update_data = {
        k: v for k, v in flight_update.model_dump().items() if v is not None
    }

    if update_data:
        try:
            if 'date_of_flight' in update_data:
                datetime.strptime(update_data['date_of_flight'], "%Y-%m-%d")
            if 'departure_time' in update_data:
                datetime.strptime(update_data['departure_time'], "%H:%M")

            result = await db.flights.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )

            if result.modified_count == 0:
                raise HTTPException(status_code=404, detail="Flight not found")

            updated_flight = await db.flights.find_one({"_id": object_id})
            updated_flight["id"] = str(updated_flight.pop("_id"))
            return updated_flight
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time"
            )
    return await get_flight(flight_id, db)


@router.delete("/{flight_id}", status_code=204)
async def delete_flight(flight_id: str, db=Depends(get_db)):
    try:
        object_id = ObjectId(flight_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid flight ID format")

    result = await db.flights.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Flight not found")


@router.get("/date/{date}", response_model=List[FlightResponse])
async def get_flights_by_date(
        date: str,
        db=Depends(get_db)
):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        flights = await db.flights.find({"date_of_flight": date}).to_list(None)

        for flight in flights:
            flight["id"] = str(flight.pop("_id"))
        return flights
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )