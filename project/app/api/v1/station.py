from fastapi import APIRouter, Depends, status, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from dependencies.database import get_session
from helpers.response import ErrorJSONResponse

router = APIRouter(prefix="/station", tags=["Station"])


@router.get(
    "/location",
    response_model=schemas.BusStationLocationResponse,
    responses={
        422: {"model": schemas.ErrorValidationResponse},
        500: {"model": schemas.ErrorResponse},
    },
    description="사용자 위치 반경 150M 이내에 존재하는 정류장을 검색한다",
)
async def get_station_location_api(
    *,
    latitude: float = Query(..., ge=-90, le=90, alias="lat", description="사용자 위치(위도)"),
    longitude: float = Query(
        ..., ge=-180, le=180, alias="lon", description="사용자 위치(경도)"
    ),
    extend: bool = Query(False, alias="extend", description="확장 검색 여부"),
    session: AsyncSession = Depends(get_session)
):
    """
    사용자 위치 반경 150M 이내에 존재하는 정류장을 검색한다

    '국토교통부_전국 버스정류장 위치정보' 데이터에서 사용자 위치를 기준으로 정류장을 검색한다
    그러나 위 데이터에는 모든 정류장 위치가 포함되어 있지 않다. 국가대중교통정보센터(TAGO)와 연계된 지자체의 버스정류장 데이터만 포함되어 있어,
    미연계되는 버스정류장은 포함되어 있지 않다.
    Link: https://market.mobilink.co.kr/search/detail/89 를 참고하면, 미연계 지자체에 '서울'이 포함되어 있어, 실제로 서울 버스정류장
    이 조회되지 않는 것이 많다.

    이를 어느정도는 해결하기 위해서 '서울 버스 운행 노선 정보' 데이터에 포함된 정류장의 데이터를 함께 사용하며 'extend' 옵션을 설정한채로 요청하면
    이 데이터에서 조회한 결과를 합쳐 반환하도록 하였다
    """

    bus_dal = crud.BusDAL(session=session)

    extend_result = []

    try:
        result = await bus_dal.get_bus_stations_by_location(
            latitude=latitude, longitude=longitude
        )
        # 확장 검색 플래그가 설정되었다면, 버스 경로 상의 정류장에서 추가로 검색한다
        if extend:
            extend_result = await bus_dal.get_bus_routes_by_location(
                latitude=latitude, longitude=longitude
            )
    except Exception as e:
        logger.exception(e)
        return ErrorJSONResponse(
            message="정류장을 검색하는 도중에 문제가 발생하였습니다",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    finally:
        await session.close()

    response = schemas.BusStationLocationResponse(
        message="ok",
        data=[
            schemas.BusStationLocation(
                location=schemas.Location(latitude=i.latitude, longitude=i.longitude),
                station_name=i.node_name,
                ars_id=i.mobile_id,
            )
            for i in result
        ],
    )

    if extend_result:
        response.data.extend(
            [
                schemas.BusStationLocation(
                    location=schemas.Location(
                        latitude=i.latitude, longitude=i.longitude
                    ),
                    station_name=i.station_name,
                    ars_id=i.ars_id,
                )
                for i in extend_result
            ]
        )
        # ARS_ID를 기준으로 중복된 정류장을 제거한다
        response.data = list({i.ars_id: i for i in response.data}.values())

    return response


@router.get(
    "/search",
    response_model=schemas.BusSearchResponse,
    responses={
        400: {"model": schemas.ErrorResponse},
        500: {"model": schemas.ErrorResponse},
    },
)
async def get_station_search_api(
    *, query: str = Query(None), session: AsyncSession = Depends(get_session)
):
    """
    버스 정류장 이름 및 버스 노선 정보로 버스 정류장을 검색한다
    """

    if not query:
        return ErrorJSONResponse(
            message="검색어를 입력해주세요",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=status.HTTP_400_BAD_REQUEST,
        )

    bus_dal = crud.BusDAL(session=session)

    try:
        #################
        # 버스정류장 조회   #
        #################
        # 버스 정류장에서 정류장 이름으로 검색한다
        bus_station_result = await bus_dal.get_bus_stations_by_node_name(
            node_name=query
        )
        # 버스 노선에서 정류장 이름으로 검색한다
        route_station_result = await bus_dal.get_bus_routes_by_station_name(
            station_name=query
        )

        #################
        # 버스 노선 조회   #
        #################
        # 버스 노선 정보에서 노선명으로 검색한다
        route_result = await bus_dal.get_bus_routes_by_route_name(route_name=query)
    except Exception as e:
        logger.exception(e)
        return ErrorJSONResponse(
            message="정류장을 검색하는 도중에 문제가 발생하였습니다",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    finally:
        await session.close()

    # 버스 정류장 정보를 합친다
    bus_station = [
        schemas.BusStationLocation(
            location=schemas.Location(latitude=i.latitude, longitude=i.longitude),
            station_name=i.node_name,
            ars_id=i.mobile_id,
        )
        for i in bus_station_result
    ]
    bus_station.extend(
        [
            schemas.BusStationLocation(
                location=schemas.Location(latitude=i.latitude, longitude=i.longitude),
                station_name=i.station_name,
                ars_id=i.ars_id,
            )
            for i in route_station_result
        ]
    )
    bus_station = sorted(
        list({i.ars_id: i for i in bus_station}.values()), key=lambda x: x.station_name
    )

    # 버스 노선 정보를 반환 형식으로 변경한다
    bus_routes = schemas.BusRoutes(routes=[])
    for i in route_result:
        # 노선명이 변경될 때마다 새로운 데이터를 생성한다
        if not bus_routes.routes or (bus_routes.routes[-1].route_name != i.route_name):
            bus_route = schemas.BusRoute(route_name=i.route_name, route=[])
            bus_routes.routes.append(bus_route)

        # 노선의 경로 정보를 추가한다
        bus_routes.routes[-1].route.append(
            schemas.Route(
                order=i.route_order,
                ars_id=i.ars_id,
                station_name=i.station_name,
                location=schemas.Location(latitude=i.latitude, longitude=i.longitude),
            )
        )

    response = schemas.BusSearchResponse(
        message="ok",
        data=schemas.BusSearch(bus_station=bus_station, bus_route=bus_routes),
    )

    return response
