from pydantic import BaseModel


class DataResponse[T](BaseModel):
    data: T
