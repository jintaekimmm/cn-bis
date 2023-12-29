from fastapi import APIRouter, Depends, Query, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from dependencies.database import get_session
from helpers.response import ErrorJSONResponse

router = APIRouter(prefix="/route", tags=["Routes"])


@router.get(
    "/search",
    response_model=schemas.BusRoutesSearchResponse,
    responses={
        400: {"model": schemas.ErrorResponse},
        500: {"model": schemas.ErrorResponse},
    },
    description="목적지를 통한 버스 노선을 조회한다",
)
async def get_route_search_api(
    *,
    destination: str = Query(None, alias="dest"),
    session: AsyncSession = Depends(get_session)
):
    """
    목적지를 통한 버스 노선을 조회한다

    목적지는 '성동구'에 한정한다.
    목적지가 서울에 한정하므로 bus_station이 아니라 bus_route에서 목적지(정류장)를 검색하고, 해당 정류장의 버스 노선 정보를 반환하도록 한다

    목적지 검색 시에, 해당 정류장을 지나가는 모든 버스 노선을 조회하므로 반환 값의 양이 엄청 커질 수 있다
    """

    if not destination:
        return ErrorJSONResponse(
            message="목적지를 입력해주세요",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=status.HTTP_400_BAD_REQUEST,
        )

    bus_dal = crud.BusDAL(session=session)

    try:
        # '성동구'의 목적지를 지나가는 버스 노선 정보를 조회한다
        routes = await bus_dal.get_bus_routes_by_destination_filter_hang_jeong_gu(
            dest=destination, hang_jeong_gu="성동구"
        )
    except Exception as e:
        logger.exception(e)
        return ErrorJSONResponse(
            message="목적지를 조회하는 도중에 문제가 발생하였습니다",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    finally:
        await session.close()

    # 노선 정보를 (목적지, 노선명, 노선 순서)로 다시 정렬한다
    sorted_routes = sorted(
        routes, key=lambda x: (x.dest_station_name, x.route_name, x.route_order)
    )

    # 목적지(정류장)별 버스 노선 정보를 반환 형식으로 변경한다
    result = []
    for i in sorted_routes:
        # 목적지(정류장)이 변경될 때마다 새로운 데이터를 생성한다
        if not result or (result[-1].station_name != i.dest_station_name):
            bus_route = schemas.BusRoutesSearch(
                station_name=i.dest_station_name, bus_route=[]
            )
            result.append(bus_route)

        # 버스 노선명이 변경될 때 마다 새로운 데이터를 생성한다
        if not result[-1].bus_route or (
            result[-1].bus_route[-1].route_name != i.route_name
        ):
            _r = schemas.BusRouteDestination(route_name=i.route_name, route=[])
            result[-1].bus_route.append(_r)

        result[-1].bus_route[-1].route.append(
            schemas.RouteDestination(
                order=i.route_order,
                ars_id=i.ars_id,
                station_name=i.station_name,
                location=schemas.Location(latitude=i.latitude, longitude=i.longitude),
                destination=i.dest,
            )
        )

    response = schemas.BusRoutesSearchResponse(message="ok", data=result)
    return response
