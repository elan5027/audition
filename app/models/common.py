from dataclasses import dataclass, field


@dataclass
class PagingDTO:
    total: int = field(default=...)
    limit: int = field(default=...)
    page: int = field(default=...)
