from dataclasses import dataclass
from fastapi import Query


@dataclass
class PageParams:
    page: int = Query(default=1, ge=1)
    limit: int = Query(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit