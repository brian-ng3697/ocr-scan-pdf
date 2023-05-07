from pydantic import BaseModel
import typing

class Response(BaseModel):
    statusCode: int
    message: str
    data: typing.Any