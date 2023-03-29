from typing import Optional

from pydantic import BaseModel, Field


class DetailsExceptionSchema(BaseModel):
    cause: Optional[str]
    message: Optional[str]

    class Config:
        orm_mode = True


class ExceptionSchema(BaseModel):
    status_code: Optional[int]
    status_msg: Optional[str]
    details: Optional[DetailsExceptionSchema]

    class Config:
        orm_mode = True


class BadRequestSchema(ExceptionSchema):
    status_code: Optional[int] = Field(example=400)


class ForbiddenSchema(ExceptionSchema):
    status_code: Optional[int] = Field(example=403)


class NotFoundSchema(ExceptionSchema):
    status_code: Optional[int] = Field(example=404)


class ValidationErrorSchema(ExceptionSchema):
    status_code: Optional[int] = Field(example=422)
