from fastapi.responses import ORJSONResponse
from typing import Generic, Optional, TypeVar, Optional
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from abc import ABC, abstractmethod
from app.models.common import PagingDTO

T = TypeVar("T")


class BaseHttpResponse(BaseModel, Generic[T]):
    message: str = "OK"
    status: str = "200"
    data: Optional[T] = None


class ErrorResponse(BaseHttpResponse):
    message: str = "Something went wrong"
    status: str = "400"


class V1HttpResponse(ORJSONResponse):
    def __init__(self, content: Optional[T] = None, **kwargs):
        super().__init__(
            content={
                "message": "OK",
                "status": "200",
                "data": content,
            },
            **kwargs
        )


class V1RequestBaseModel(BaseModel, ABC):
    @abstractmethod
    def to_dto(self) -> "V1RequestBaseModel":
        pass


class V1RequestQueryModel:
    @abstractmethod
    def from_query(self) -> "V1RequestBaseModel":
        pass


@dataclass
class Paging:
    total: int
    limit: int
    page: int

    @classmethod
    def from_dto(cls, dto: PagingDTO) -> "Paging":
        return cls(total=dto.total, limit=dto.limit, page=dto.page)
