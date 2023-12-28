from geopandas import GeoDataFrame
from sqlalchemy import delete, insert

from crud.abstract import DalABC
from models import HangJeongGu


class AddressDAL(DalABC):
    async def delete_hang_jeong_gu(self):
        """
        hang_jeong_gu table 데이터를 삭제한다

        :return:
        """

        q = delete(HangJeongGu).execution_options(synchronize_session="fetch")

        await self.session.execute(q)

    async def bulk_insert_hang_jeong_gu(self, gdf: GeoDataFrame):
        """
        hang_jeong_gu 데이터를 bulk insert 한다

        :param gdf:
        :return:
        """

        q = insert(HangJeongGu)

        await self.session.execute(
            q,
            [
                {
                    "sig_code": row["sig_code"],
                    "sido": row["sido"],
                    "sig_eng_name": row["sig_eng_name"],
                    "sig_kor_name": row["sig_kor_name"],
                    "geometry": str(row["geometry"]),
                }
                for row in gdf.to_dict(orient="records")
            ],
        )
