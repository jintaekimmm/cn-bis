from geoalchemy2 import Geometry
from sqlalchemy import Column, BigInteger, String, Integer, DATE

from connection.database import Base
from models.mixin import TimestampMixin


class BusRoute(Base, TimestampMixin):
    __tablename__ = "bus_route"

    id = Column(BigInteger, primary_key=True, index=True)
    route_id = Column(BigInteger)
    route_name = Column(String(32), index=True)
    route_order = Column(Integer)
    node_id = Column(BigInteger)
    ars_id = Column(BigInteger, index=True)
    station_name = Column(String(255), index=True)
    location = Column(Geometry(geometry_type="POINT", srid=4326, spatial_index=True))


class BusStation(Base, TimestampMixin):
    __tablename__ = "bus_station"

    id = Column(BigInteger, primary_key=True, index=True)
    node_id = Column(String(64))
    node_name = Column(String(128), index=True)
    location = Column(Geometry(geometry_type="POINT", srid=4326, spatial_index=True))
    collectd_time = Column(DATE)
    mobile_id = Column(BigInteger, index=True)
    city_code = Column(BigInteger)
    city_name = Column(String(16))
    admin_name = Column(String(16))
