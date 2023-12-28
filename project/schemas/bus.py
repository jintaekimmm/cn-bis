from pydantic import BaseModel

from schemas import DefaultResponse


class Location(BaseModel):
    latitude: float
    longitude: float


class BusSearch(BaseModel):
    location: Location
    station_name: str
    ars_id: int


class BusSearchResponse(DefaultResponse):
    data: list[BusSearch]
