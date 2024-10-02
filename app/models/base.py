from sqlalchemy.ext.declarative import as_declarative
from typing import Any


@as_declarative()
class Base:
    id: Any
    __name__: str
