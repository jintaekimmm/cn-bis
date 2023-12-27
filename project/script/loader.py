import asyncio
import pathlib
import time

import pandas as pd
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


async def main():
    # 버스 정류소 데이터를 불러온다
    station_df = pd.read_csv(f"{BASE_DIR}/data/bus_station.csv", encoding="utf-8")
    # 버스 경로 데이터를 불러온다
    route_df = pd.read_csv(f"{BASE_DIR}/data/bus_route.csv", encoding="utf-8")

    # Database Session
    session = async_session()

    loader_dal = crud.LoaderDAL(session)

    try:
        await process_station_table(loader_dal, station_df)
        await process_route_table(loader_dal, route_df)

        await session.commit()
    except Exception as e:
        await session.rollback()
        del route_df
        del station_df

        raise Exception(e)
    finally:
        await session.close()


if __name__ == "__main__":
    start_time = time.time()
    logger.info("Bus data load start...")
    asyncio.run(main())
    end_time = time.time()
    logger.info(
        f"Bus data load complete. Elapsed Time is {end_time - start_time} seconds."
    )
