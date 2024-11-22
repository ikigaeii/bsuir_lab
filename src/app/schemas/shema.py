from typing import List, Optional
from pydantic import BaseModel


class Flight(BaseModel):
    departure_time: str
    date_of_flight: str


class FlightCreate(Flight):
    pass


class FlightUpdate(Flight):
    departure_time: Optional[str] = None
    date_of_flight: Optional[str] = None


class FlightResponse(Flight):
    id: str
    departure_time: str
    date_of_flight: str

    class Config:
        from_attributes = True
        json_encoders = {int: str}


# === Passport Schemas ===
class PassportBase(BaseModel):
    passport_number: str
    firstname: str
    lastname: str


class PassportCreate(PassportBase):
    pass


class PassportResponse(PassportBase):
    id: str

    class Config:
        from_attributes = True


# === Client Schemas ===
class ClientBase(BaseModel):
    mail: str
    phone_number: str
    nick_name: str


class ClientCreate(ClientBase):
    passport_id: str
    reservation_ids: Optional[List[str]] = []



class ClientResponse(ClientBase):
    id: str
    passport_id: str
    reservation_ids: Optional[List[str]] = []

    class Config:
        from_attributes = True


# === Reservation Schemas ===
class ReservationBase(BaseModel):
    status: str
    date_of_registration: str
    total_cost: int
    flight_id: str
    client_id: str
    passport_id: List[str]


class ReservationCreate(ReservationBase):
    pass


class ReservationResponse(ReservationBase):
    id: str
    flight: Optional[FlightResponse] = None
    client: Optional[ClientResponse] = None
    passports: Optional[List[PassportResponse]] = []

    class Config:
        from_attributes = True


class ReservationFull(ReservationResponse):
    flight: FlightResponse
    client: ClientResponse
    passports: List[PassportResponse]

    class Config:
        from_attributes = True
