from fastapi import Depends, HTTPException, APIRouter, BackgroundTasks, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from fastapi.responses import ORJSONResponse, Response, JSONResponse, RedirectResponse
from app.db.schemas.user import (
    UserCreateReq,
    UserResp,
    VerifyCodeInput,
    Profile,
    UserLoginReq,
)
from app.core.redis import RedisCache
from app.core.containers import Container
from app.services.user_service import UserService
from dependency_injector.wiring import Provide, inject
from app.db.schemas.common import (
    BaseHttpResponse,
    V1HttpResponse,
    ErrorResponse,
    Paging,
)
import secrets

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

# MANAGER("ROLE_MANGER","중간 관리자"),
# ADMIN("ROLE_ADMIN", "최고 관리자"),
# MEMBER("ROLE_MEMBER","일반 사용자")

# ACTIVE
# INACTIVE

# 암복호화 모듈을 sisa.seedpb


@router.post(
    "/join",
    response_model=BaseHttpResponse[str],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def join(
    admin: UserCreateReq,
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> BaseHttpResponse[str]:
    await user_service.add_user(admin)
    return V1HttpResponse(content="Signup Success")


@router.post(
    "/login",
    responses={400: {"model": ErrorResponse}},
)
@inject
async def login(
    response: Response,
    form_data: UserLoginReq,
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> JSONResponse:
    access_token = await user_service.login_user(form_data.email, form_data.password)
    response.headers["auth"] = access_token
    response.set_cookie(key="auth", value=access_token)
    json_response = JSONResponse(content={"message": "Login Success"})

    for key, value in response.headers.items():
        json_response.headers[key] = value

    return json_response


@router.get(
    "/me",
    response_model=BaseHttpResponse[UserResp],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def me(
    auth: str = Cookie(None),
    # token: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> BaseHttpResponse[UserResp]:
    user = await user_service.verify_token(auth)
    admin = await user_service.get_user_data(user.id)
    return V1HttpResponse(content=admin)


@router.get(
    "/profile",
    response_model=BaseHttpResponse[Profile],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def is_profile(
    auth: str = Cookie(None),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> BaseHttpResponse[Profile]:
    user = await user_service.verify_token(auth)
    admin = await user_service.get_user_profile(user.id)
    return V1HttpResponse(content=admin)


@router.put(
    "/profile/update",
    response_model=BaseHttpResponse[UserResp],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def put_profile(
    profile: Profile,
    auth: str = Cookie(None),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> BaseHttpResponse[UserResp]:
    user = await user_service.verify_token(auth)
    admin = await user_service.update_user_profile(user.id, profile)

    return V1HttpResponse(content=Profile.from_dto(admin))


@router.post(
    "/profile/create",
    response_model=BaseHttpResponse[UserResp],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def create_profile(
    profile: Profile,
    auth: str = Cookie(None),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> BaseHttpResponse[UserResp]:
    user = await user_service.verify_token(auth)
    admin = await user_service.create_user_profile(user.id, profile)

    return V1HttpResponse(content=Profile.from_dto(admin))


@router.get(
    "/list",
    response_model=BaseHttpResponse[List[UserResp]],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def list_admins(
    auth: str = Cookie(None),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> BaseHttpResponse[List[UserResp]]:
    await user_service.verify_token(auth)
    admins = await user_service.get_users_data()
    return V1HttpResponse(
        content=admins,
    )


@router.get(
    "/list/{admin_id}",
    response_model=BaseHttpResponse[UserResp],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def read_admin(
    admin_id: int,
    auth: str = Cookie(None),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> BaseHttpResponse[UserResp]:
    await user_service.verify_token(auth)
    db_admin = await user_service.get_user_data(admin_id)
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return V1HttpResponse(content=db_admin)


# @router.get("/email/create")
# @inject
# async def verify_email(
#     email: str,
#     background_tasks: BackgroundTasks,
#     user_service: UserService = Depends(Provide[Container.user_service]),
#     cache: RedisCache = Depends(Provide[Container.redis_cache]),
# ) -> BaseHttpResponse[UserResp]:

#     token = secrets.token_hex(4)
#     await cache.set(f"verification:{email}", token, ttl=300)

#     background_tasks.add_task(
#         user_service.smtp_client.send_verification_email, to_email=email, token=token
#     )
#     return V1HttpResponse(content=token)


# @router.post("/email/verify")
# @inject
# async def verify_email(
#     input_data: VerifyCodeInput,
#     cache: RedisCache = Depends(Provide[Container.redis_cache]),
# ) -> BaseHttpResponse[UserResp]:
#     saved_code = await cache.get(f"verification:{input_data.email}")
#     if not saved_code:
#         raise HTTPException(status_code=400, detail="인증 요청을 찾을 수 없습니다.")

#     if saved_code != input_data.code:
#         raise HTTPException(status_code=400, detail="인증 코드가 잘못되었습니다.")

#     return V1HttpResponse(content="Success")
