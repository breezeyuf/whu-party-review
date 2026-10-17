from __future__ import annotations

from typing import Any, Optional

from fastapi import HTTPException


class AppError(HTTPException):
    def __init__(self, status: int, code: int, message: str, data: Any = None):
        super().__init__(status_code=status, detail={"code": code, "message": message, "data": data})
        self.biz_code = code
        self.biz_message = message
        self.biz_data = data


def bad_request(message: str, data: Any = None) -> AppError:
    return AppError(400, 40000, message, data)


def unauthorized(message: str = "未登录或登录已失效") -> AppError:
    return AppError(401, 40100, message)


def forbidden(message: str = "无权限", code: int = 40300) -> AppError:
    return AppError(403, code, message)


def not_found(message: str = "对象不存在") -> AppError:
    return AppError(404, 40400, message)


def conflict(message: str, code: int = 40900, data: Any = None) -> AppError:
    return AppError(409, code, message, data)


def too_large(message: str = "文件过大") -> AppError:
    return AppError(413, 41300, message)


def unsupported(message: str = "文件类型不符") -> AppError:
    return AppError(415, 41500, message)


def unprocessable(message: str, errors: Optional[list] = None) -> AppError:
    return AppError(422, 42200, message, {"errors": errors or []})


def locked(message: str, data: Any = None) -> AppError:
    return AppError(423, 42300, message, data)


def gone(message: str = "文件已过期") -> AppError:
    return AppError(410, 41000, message)
