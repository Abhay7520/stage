"""JSON-safe validation errors, including malformed nonfinite JSON numbers."""

import math
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {k: safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


async def validation_error_handler(request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": safe(exc.errors())})
