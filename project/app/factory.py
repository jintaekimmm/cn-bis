from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1 import station, route
from connection.database import engine
from helpers.response import ErrorJSONResponse, DefaultJSONResponse


def create_app() -> FastAPI:
    """Create FastAPI Application"""

    app = FastAPI(
        title="cn-bis API",
        summary="cn-bis APIs",
        version="0.0.1",
    )

    initial_route(app)
    initial_middleware(app)
    set_custom_exception(app)
    set_event_handler(app)

    return app


def set_event_handler(app: FastAPI) -> None:
    """Event Handlers"""

    @app.on_event("startup")
    async def startup():
        # Database
        async with engine.begin():
            pass

    @app.on_event("shutdown")
    async def shutdown():
        # Database
        if engine:
            await engine.dispose()


def initial_route(app: FastAPI) -> None:
    """Routes Initializing"""

    @app.get("/")
    async def root():
        return DefaultJSONResponse(message="ok")

    @app.get("/health")
    async def health_check():
        return DefaultJSONResponse(message="ok")

    app.include_router(station.router, prefix="/v1")
    app.include_router(route.router, prefix="/v1")


def initial_middleware(app: FastAPI) -> None:
    """Middleware Initializing"""

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def set_custom_exception(app: FastAPI) -> None:
    """Custom Exception Handlers"""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """
        RequestValidation Handler

        HTTP Status 422(UNPROCESSABLE_ENTITY)의 error logging을 위한 exception handler이다
        error response만 logging하고 원래 형식으로 결과를 반환한다

        2023-07-10 13:11:13.098 ERROR app.factory:validation_exception_handler:164 validation error:
        [{'type': 'value_error', 'loc': ('body', 'password'), 'msg': 'Value error, 8자리 이상의 소문자/대문자/숫자/기호 중 두 가지 이상의 종류를 포함해야합니다', 'input': '1', 'ctx': {'error': '8자리 이상합니다'}, 'url': 'https://errors.pydantic.dev/2.1.2/v/value_error'}]
        """

        logger.error(f"validation error: {exc.errors()}")
        errors = []
        for error in exc.errors():
            try:
                # error message가 다음과 같이 error Type명을 처음에 포함하고 있으므로, 이를 제거한다
                # -> Value error, 비밀번호는 필수로 입력해야 합니다
                if "error" in error.get("msg", "").split(",")[0]:
                    new_error_msg = "".join(error.get("msg", "").split(",")[1:])
                else:
                    new_error_msg = error["msg"]
            except Exception:
                new_error_msg = error["msg"]

            errors.append({"field": error["loc"][-1], "message": new_error_msg.strip()})

        return ErrorJSONResponse(
            message=errors,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=422,
        )
