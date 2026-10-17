from __future__ import annotations

from datetime import date, datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: T | None = None


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def ok(data: Any = None, message: str = "ok") -> dict:
    return {"code": 0, "message": message, "data": data if data is not None else {}}


def page_params(page: int = 1, page_size: int = 20) -> tuple[int, int]:
    page = min(max(1, page or 1), 100000)
    page_size = min(200, max(1, page_size or 20))
    return page, page_size


def iso(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        from datetime import timezone, timedelta

        dt = dt.replace(tzinfo=timezone(timedelta(hours=8)))
    return dt.isoformat()


def dstr(d: Optional[date]) -> Optional[str]:
    return d.isoformat() if d else None
