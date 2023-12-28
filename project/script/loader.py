import asyncio
import pathlib
import time

import pandas as pd
import geopandas as gpd
from loguru import logger

import crud
from connection.database import async_session

BASE_DIR = pathlib.Path(__file__).parent.parent


async def process_route_table(loader_dal: crud.LoaderDAL, df: pd.DataFrame) -> None:
    """
    bus_route 테이블 데이터를 삭제하고 다시 추가한다

    :param loader_dal:
    :param df:
    :return:
    """

    # 저장되어 있는 데이터를 삭제한다
    await loader_dal.delete_route()
    # bus route 데이터를 삽입한다
    await loader_dal.bulk_insert_route(df)


async def process_station_table(loader_dal: crud.LoaderDAL, df: pd.DataFrame) -> None:
    """
    bus_station 테이블 데이터를 삭제하고 다시 추가한다

    :param loader_dal:
    :param df:
    :return:
    """

    # 저장되어 있는 데이터를 삭제한다
    await loader_dal.delete_station()
    # bus station 데이터를 삽입한다
    await loader_dal.bulk_insert_station(df)


async def process_hang_jeong_gu_table(
    address_dal: crud.AddressDAL, gdf: gpd.GeoDataFrame
) -> None:
    """
    hang_jeong_gu 테이블에 데이터를 삭제하고 다시 추가한다
    여기서는 모든 지역을 추가하지 않고 '서울' 지역의 시/구 데이터만 넣어서 확인한다

    :param address_dal:
    :param gdf:
    :return:
    """

    # 저장되어 있는 데이터를 삭제한다
    await address_dal.delete_hang_jeong_gu()
    # 시/구 데이터를 삽입한다
    await address_dal.bulk_insert_hang_jeong_gu(gdf)


async def main():
    # 시/구 데이터를 불러온다
    gdf = gpd.read_file(f"{BASE_DIR}/data/geo/hang_jeong_gu.geojson")
    # 버스 정류소 데이터를 불러온다
    station_df = pd.read_csv(f"{BASE_DIR}/data/bus/bus_station.csv", encoding="utf-8")
    # 버스 경로 데이터를 불러온다
    route_df = pd.read_csv(f"{BASE_DIR}/data/bus/bus_route.csv", encoding="utf-8")

    # Database Session
    session = async_session()

    loader_dal = crud.LoaderDAL(session)
    address_dal = crud.AddressDAL(session)

    try:
        await process_hang_jeong_gu_table(address_dal, gdf)
        await process_station_table(loader_dal, station_df)
        await process_route_table(loader_dal, route_df)

        await session.commit()
    except Exception as e:
        await session.rollback()

        raise Exception(e)
    finally:
        await session.close()


if __name__ == "__main__":
    start_time = time.time()
    logger.info("data load start...")
    asyncio.run(main())
    end_time = time.time()
    logger.info(f"data load complete. Elapsed Time is {end_time - start_time} seconds.")
