from abc import ABCMeta

from pydantic import BaseModel


class ResponseSchemaABC(BaseModel, metaclass=ABCMeta):
    pass


class DefaultResponse(ResponseSchemaABC):
    message: str


class ErrorMessage(BaseModel):
    message: str
    code: str


class ValidationMessage(BaseModel):
    field: str
    message: str


class ErrorValidationMessage(BaseModel):
    message: list[ValidationMessage]


class ErrorResponse(ResponseSchemaABC):
    """
    Error Response Format을 위한 스키마
    """

    error: ErrorMessage


class ErrorValidationResponse(ResponseSchemaABC):
    """
    ValidationError Response Format을 위한 스키마
    """

    error: ErrorValidationMessage
