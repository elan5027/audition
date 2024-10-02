from fastapi import Depends, HTTPException, APIRouter, Request, Cookie
from sqlalchemy.orm import Session
from app.core.containers import Container
from app.services.user_service import UserService
from app.services.image_service import ImageService
from app.db.schemas.course import AWSReq
from dependency_injector.wiring import Provide, inject
from app.db.schemas.common import (
    BaseHttpResponse,
    ErrorResponse,
    V1HttpResponse,
)

router = APIRouter()


@router.api_route(
    methods=["post", "put", "delete"],
    path="/s3/url",
    response_model=BaseHttpResponse[dict],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def put_presign(
    object_key: AWSReq,
    request: Request,
    auth: str = Cookie(None),
    user_service: UserService = Depends(Provide[Container.user_service]),
    image_service: ImageService = Depends(Provide[Container.image_service]),
) -> BaseHttpResponse[dict]:
    print("Method : ", request.method)

    method_map = {"post": "get_object", "put": "put_object", "delete": "delete_object"}
    method = method_map.get(request.method.lower())
    if not method:
        raise HTTPException(status_code=400, detail="None")
    user = await user_service.verify_token(auth)
    # user.id
    # directory = temp/{round_id}/{user_id}/filename
    _object_key = f"{object_key.directory}/{user.id}/{object_key.file_name}"
    url = image_service.create_presing(_object_key, method)
    return V1HttpResponse(content={"url": url})
