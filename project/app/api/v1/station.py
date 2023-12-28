from fastapi import APIRouter, Depends, status, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

import crud
import schemas
from dependencies.database import get_session
from helpers.response import ErrorJSONResponse

router = APIRouter(prefix="/station", tags=["Station"])


@router.get(
    "/search",
    response_model=schemas.BusSearchResponse,
    responses={
        422: {"model": schemas.ErrorValidationResponse},
        500: {"model": schemas.ErrorResponse},
    },
    description="사용자 위치 반경 150M 이내에 존재하는 정류장을 검색한다",
)
async def search_station_api(
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
        result = await bus_dal.get_stations_by_location(
            latitude=latitude, longitude=longitude
        )
        # 확장 검색 플래그가 설정되었다면, 버스 경로 상의 정류장에서 추가로 검색한다
        if extend:
            extend_result = await bus_dal.get_stations_extend_by_route(
                latitude=latitude, longitude=longitude
            )
    except Exception as e:
        logger.exception(e)
        await session.rollback()
        return ErrorJSONResponse(
            message="정류장을 검색하는 도중에 문제가 발생하였습니다",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    finally:
        await session.close()

    response = schemas.BusSearchResponse(
        message="ok",
        data=[
            schemas.BusSearch(
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
                schemas.BusSearch(
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
