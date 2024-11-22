from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId


class BaseMongoModel(BaseModel):
    id: int = Field(default_factory=int, alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {int: str}
        from_attributes = True
        arbitrary_types_allowed = True


class PassportModel(BaseMongoModel):
    passport_number: str
    firstname: str
    lastname: str


class ClientModel(BaseMongoModel):
    mail: str
    phone_number: str
    nick_name: str
    passport_id: str
    reservation: Optional[List[PassportModel]] = []


class FlightModel(BaseMongoModel):
    departure_time: str
    date_of_flight: str


class ReservationModel(BaseMongoModel):
    status: str
    date_of_registration: str
    total_cost: int
    flight_id: str
    client_id: str
    passport_id: List[str]
