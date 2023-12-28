import pandas as pd
from sqlalchemy import select, delete, insert, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.abstract import DalABC
from models import BusRoute, BusStation


class LoaderDAL(DalABC):
    async def bulk_insert_route(self, df: pd.DataFrame) -> None:
        """
        bus_route 데이터를 bulk insert 한다

        :param df: bus route 정보를 가지고 있는 DataFrame
        :return:
        """

        q = insert(BusRoute)

        await self.session.execute(
            q,
            [
                {
                    "route_id": row["route_id"],
                    "route_name": row["route_name"],
                    "route_order": row["route_order"],
                    "node_id": row["node_id"],
                    "ars_id": row["ars_id"],
                    "station_name": row["station_name"],
                    "location": f"POINT({row['latitude']} {row['longitude']})",
                }
                for row in df.to_dict(orient="records")
            ],
        )

    async def bulk_insert_station(self, df: pd.DataFrame) -> None:
        """
        bus_station 데이터를 bulk insert 한다

        :param df: bus station 정보를 가지고 있는 DataFrame
        :return:
        """

        q = insert(BusStation)

        await self.session.execute(
            q,
            [
                {
                    "node_id": row["node_id"],
                    "node_name": row["node_name"],
                    "location": f"POINT({row['latitude']} {row['longitude']})",
                    "collectd_time": row["collectd_time"],
                    "mobile_id": row["mobile_id"],
                    "city_code": row["city_code"],
                    "city_name": row["city_name"],
                    "admin_name": row["admin_name"],
                }
                for row in df.to_dict(orient="records")
            ],
        )

    async def delete_route(self) -> None:
        """
        bus_route table 데이터를 삭제한다

        :return:
        """

        q = delete(BusRoute).execution_options(synchronize_session="fetch")

        await self.session.execute(q)

    async def delete_station(self) -> None:
        """
        bus_station table 데이터를 삭제한다

        :return:
        """

        q = delete(BusStation).execution_options(synchronize_session="fetch")

        await self.session.execute(q)


class BusDAL(DalABC):
    def __init__(self, session: AsyncSession) -> None:
        self.SRID = 4326
        super().__init__(session=session)

    async def get_stations_by_location(
        self, latitude: float, longitude: float, distance: int = 150
    ):
        """
        사용자 위치를 기준으로 정류장을 조회한다

        :param latitude: 사용자 위치(위도)
        :param longitude: 사용자 위치(경도)
        :param distance: 사용자 기준 반경 거리(단위 M)
        :return:
        """

        # 사용자 위치 기준으로 반경 거리만큼 원을 그린다
        buffer_circle = func.ST_Buffer(
            func.ST_PointFromText(f"POINT({latitude} {longitude})", self.SRID), distance
        )

        q = select(
            BusStation.node_name,
            func.ST_X(BusStation.location).label("latitude"),
            func.ST_Y(BusStation.location).label("longitude"),
            BusStation.mobile_id,
        ).where(func.ST_Contains(buffer_circle, BusStation.location))

        result = await self.session.execute(q)
        return result.all()

    async def get_stations_extend_by_route(
        self, latitude: float, longitude: float, distance: int = 150
    ):
        """
        사용자 위치를 기준으로 버스 경로에서 정류장을 조회한다

        :param latitude:  사용자 위치(위도)
        :param longitude:  사용자 위치(경도)
        :param distance: 사용자 기준 반경 거리(M)
        :return:
        """

        # 사용자 위치 기준으로 반경 거리만큼 원을 그린다
        buffer_circle = func.ST_Buffer(
            func.ST_PointFromText(f"POINT({latitude} {longitude})", self.SRID), distance
        )

        q = (
            select(
                BusRoute.station_name,
                func.ST_X(BusRoute.location).label("latitude"),
                func.ST_Y(BusRoute.location).label("longitude"),
                BusRoute.ars_id,
            )
            .where(func.ST_Contains(buffer_circle, BusRoute.location))
            .group_by(BusRoute.ars_id, BusRoute.station_name, BusRoute.location)
        )

        result = await self.session.execute(q)
        return result.all()
