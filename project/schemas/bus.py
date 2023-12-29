from pydantic import BaseModel

from schemas import DefaultResponse


class Location(BaseModel):
    latitude: float
    longitude: float


class BusStationLocation(BaseModel):
    location: Location
    station_name: str
    ars_id: int


class BusStationLocationResponse(DefaultResponse):
    data: list[BusStationLocation]


class Route(BaseModel):
    order: int
    ars_id: int
    station_name: str
    location: Location


class RouteDestination(Route):
    destination: bool


class BusRoute(BaseModel):
    route_name: str
    route: list[Route]


class BusRouteDestination(BusRoute):
    route: list[RouteDestination]


class BusRoutes(BaseModel):
    routes: list[BusRoute]


class BusSearch(BaseModel):
    bus_station: list[BusStationLocation]
    bus_route: BusRoutes


class BusSearchResponse(DefaultResponse):
    data: BusSearch


class BusRoutesSearch(BaseModel):
    bus_route: list[BusRouteDestination]
    station_name: str


class BusRoutesSearchResponse(DefaultResponse):
    data: list[BusRoutesSearch]
