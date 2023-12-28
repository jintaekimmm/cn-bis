import pandas as pd
from sqlalchemy import select, delete, insert

from crud.abstract import DalABC
from models import BusRoute, BusStation


class LoaderDAL(DalABC):
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


class BusDAL(DalABC):
    ...
