from typing import Any, Dict

from fastapi import HTTPException, Request
from fastapi.responses import ORJSONResponse


HTTP_400_SESSION_EXPIRED = "BM40000"
HTTP_401_UNAUTHORIZED = "BM40100"
HTTP_403_PERMISSION_DENIED = "BM40300"
HTTP_500_REDIS_LOCK_FAILED = "BM50000"

MESSAGE_CONTAIN_IMAGE_URL = "Problem includes an image"
MESSAGE_IMAGE_UPLOAD_FAILED = "Image upload failed"
MESSAGE_INVALID_IMAGE_FORMAT = "Invalid image format (png, jpg, jpeg, pdf)"


class APIException(Exception):
    def __init__(self, code: str, message: str = None):
        self.code = code
        self.message = message

    def get_error_message(self) -> Dict[str, Any]:
        return {
            "statusCode": self.code,
            "message": self.message,
        }


class APIAuthException(Exception):
    def __init__(self, code: str, message: str = None):
        self.code = code
        self.message = message


class ForbiddenException(Exception):
    def __init__(self, code: str, message: str = None):
        self.code = code
        self.message = message


class UnauthorizedException(APIAuthException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(code=HTTP_401_UNAUTHORIZED, message=message)


async def api_error_handler(_: Request, exc: APIException) -> ORJSONResponse:
    print("error : ", exc)
    return ORJSONResponse(
        headers={"x-error-code": exc.code},
        content={
            "statusCode": exc.code,
            "message": exc.message,
        },
        status_code=400,
    )


async def auth_error_handler(_: Request, exc: APIAuthException) -> ORJSONResponse:
    return ORJSONResponse(
        headers={"x-error-code": exc.code},
        content={
            "statusCode": exc.code,
            "message": exc.message,
        },
        status_code=401,
    )


class PermissionDeniedException(ForbiddenException):
    def __init__(self):
        super().__init__(code=HTTP_403_PERMISSION_DENIED, message="Permission Denied")


async def forbidden_error_handler(
    _: Request, exc: ForbiddenException
) -> ORJSONResponse:
    return ORJSONResponse(
        headers={"x-error-code": exc.code},
        content={
            "statusCode": exc.code,
            "message": exc.message,
        },
        status_code=403,
    )
