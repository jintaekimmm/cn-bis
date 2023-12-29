from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, BigInteger

from connection.database import Base
from models.mixin import TimestampMixin


class HangJeongGu(Base, TimestampMixin):
    __tablename__ = "hang_jeong_gu"

    id = Column(BigInteger, primary_key=True, index=True)
    sig_code = Column(Integer)
    sido = Column(String(32))
    sig_eng_name = Column(String(64))
    sig_kor_name = Column(String(64), index=True)
    geometry = Column(Geometry(geometry_type="POLYGON", spatial_index=True, srid=4326))
