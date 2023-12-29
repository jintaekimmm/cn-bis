import pandas as pd
from sqlalchemy import select, delete, insert, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from crud.abstract import DalABC
from models import BusRoute, BusStation, HangJeongGu


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

    async def get_bus_stations_by_location(
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

    async def get_bus_routes_by_location(
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

    async def get_bus_stations_by_node_name(self, node_name: str):
        """
        버스 정류장 이름으로 정류장을 조회한다

        :param node_name: 버스 정류장 이름
        :return:
        """

        q = select(
            BusStation.node_name,
            func.ST_X(BusStation.location).label("latitude"),
            func.ST_Y(BusStation.location).label("longitude"),
            BusStation.mobile_id,
        ).where(BusStation.node_name.like(f"%{node_name}%"))

        result = await self.session.execute(q)
        return result.all()

    async def get_bus_routes_by_station_name(self, station_name: str):
        """
        버스 정류장 이름으로 정류장을 조회한다

        :param station_name: 버스 정류장 이름
        :return:
        """

        q = (
            select(
                BusRoute.station_name,
                func.ST_X(BusRoute.location).label("latitude"),
                func.ST_Y(BusRoute.location).label("longitude"),
                BusRoute.ars_id,
            )
            .where(BusRoute.station_name.like(f"%{station_name}%"))
            .group_by(BusRoute.ars_id, BusRoute.station_name, BusRoute.location)
        )

        result = await self.session.execute(q)
        return result.all()

    async def get_bus_routes_by_route_name(self, route_name: str):
        """
        버스 노선명으로 버스 노선 정보를 조회한다

        :param route_name: 버스 노선명
        :return:
        """

        q = (
            select(
                BusRoute.route_name,
                BusRoute.route_order,
                BusRoute.ars_id,
                BusRoute.station_name,
                func.ST_X(BusRoute.location).label("latitude"),
                func.ST_Y(BusRoute.location).label("longitude"),
            )
            .where(BusRoute.route_name.like(f"%{route_name}%"))
            .order_by(BusRoute.route_name, BusRoute.route_order)
        )

        result = await self.session.execute(q)
        return result.all()

    async def get_bus_routes_by_destination_filter_hang_jeong_gu(
        self, dest: str, hang_jeong_gu: str
    ):
        """
        특정 시/구의 목적지(정류장)를 지나가는 버스 노선을 조회한다

        :param dest: 목적지(정류장) 이름
        :param hang_jeong_gu: 목적지가 포함되는 지역 '구'의 이름
        :return:
        """

        br = aliased(BusRoute)
        brt = aliased(BusRoute)
        hjg = aliased(HangJeongGu)

        q = (
            select(
                brt.route_name,
                brt.route_order,
                func.ST_X(brt.location).label("latitude"),
                func.ST_Y(brt.location).label("longitude"),
                brt.station_name,
                brt.ars_id,
                br.ars_id.label("dest_ars_id"),
                br.station_name.label("dest_station_name"),
                (case((brt.ars_id == br.ars_id, True), else_=False)).label("dest"),
            )
            .join(brt, br.route_name == brt.route_name)
            .join(hjg, func.ST_Within(br.location, hjg.geometry))
            .where(br.station_name.like(f"%{dest}%"), hjg.sig_kor_name == hang_jeong_gu)
            .group_by(
                brt.route_name,
                brt.route_order,
                brt.location,
                brt.station_name,
                brt.ars_id,
                br.ars_id,
                br.station_name,
            )
        )

        result = await self.session.execute(q)
        return result.all()
