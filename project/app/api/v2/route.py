from fastapi import APIRouter, Query, Depends, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from dependencies.database import get_session
from helpers.response import ErrorJSONResponse

router = APIRouter(prefix="/route", tags=["Routes"])


@router.get(
    "/search",
    response_model=schemas.BusRouteNameResponse,
    responses={
        400: {"model": schemas.ErrorResponse},
        500: {"model": schemas.ErrorResponse},
    },
    description="목적지를 통한 버스 노선명을 조회한다",
)
async def get_route_name_search_api(
    *,
    destination: str = Query(None, alias="dest"),
    session: AsyncSession = Depends(get_session)
):
    """
    목적지를 통한 버스 노선명을 조회한다

    목적지는 '성동구'에 한정한다.
    목적지가 서울에 한정하므로 bus_station이 아니라 bus_route에서 목적지(정류장)를 검색하고, 해당 정류장의 버스 노선명을 반환하도록 한다
    """

    if not destination:
        return ErrorJSONResponse(
            message="목적지를 입력해주세요",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=status.HTTP_400_BAD_REQUEST,
        )

    bus_dal = crud.BusDAL(session=session)

    try:
        routes = await bus_dal.get_bus_route_name_by_destination_filter_hang_jeong_gu(
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

    response = schemas.BusRouteNameResponse(
        message="ok",
        data=[
            schemas.BusRouteName(route_id=i.route_id, route_name=i.route_name)
            for i in routes
        ],
    )
    return response


@router.get(
    "/node/search",
    response_model=schemas.BusRouteNodeResponse,
    responses={
        400: {"model": schemas.ErrorResponse},
        500: {"model": schemas.ErrorResponse},
    },
)
async def get_route_node_search_api(
    *, node: str = Query(None), session: AsyncSession = Depends(get_session)
):
    """
    버스 노선명의 노선 정보를 조회한다

    '성동구'에 한정하여 조회하므로 버스 노선 중에 정류장이 '성동구'가 포함되어 있어야 한다
    """

    if not node:
        return ErrorJSONResponse(
            message="버스 노선을 입력해주세요",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=status.HTTP_400_BAD_REQUEST,
        )

    bus_dal = crud.BusDAL(session=session)

    try:
        routes = await bus_dal.get_bus_route_by_route_name_filter_hang_jeong_gu(
            route_name=node, hang_jeong_gu="성동구"
        )
    except Exception as e:
        logger.exception(e)
        return ErrorJSONResponse(
            message="노선을 조회하는 도중에 문제가 발생하였습니다",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    finally:
        await session.close()

    result = [
        schemas.Route(
            order=i.route_order,
            ars_id=i.ars_id,
            station_name=i.station_name,
            location=schemas.Location(latitude=i.latitude, longitude=i.longitude),
        )
        for i in routes
    ]
    response = schemas.BusRouteNodeResponse(
        message="ok", data=schemas.BusRoute(route_name=node, route=result)
    )

    return response
