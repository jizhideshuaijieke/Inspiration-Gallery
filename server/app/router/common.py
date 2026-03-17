from uuid import uuid4

from fastapi.responses import JSONResponse


def ok(data: dict):
    return {
        "code": 0,
        "message": "ok",
        "data": data,
        "request_id": str(uuid4()),
    }


def error(code: int, message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "data": None,
            "request_id": str(uuid4()),
        },
    )
