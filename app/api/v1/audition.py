from fastapi import Depends, HTTPException, APIRouter, Request, Cookie
from sqlalchemy.orm import Session
from app.core.containers import Container
from app.services.user_service import UserService
from app.services.audition_service import AuditionService
from app.db.schemas.course import AuditionResp, RoundResp
from app.db.schemas.user import ApplyProfile
from dependency_injector.wiring import Provide, inject
from app.db.schemas.common import (
    BaseHttpResponse,
    ErrorResponse,
    V1HttpResponse,
)

router = APIRouter()


@router.post(
    path="/create",
    response_model=BaseHttpResponse[AuditionResp],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def create_auditon(
    audition_data: AuditionResp,
    audition_service: AuditionService = Depends(Provide[Container.audition_service]),
):
    auditons = await audition_service.create_auditions(audition_data)
    return V1HttpResponse(content=auditons)


@router.get(
    path="/list",
    response_model=BaseHttpResponse[AuditionResp],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def get_auditon_list(
    audition_service: AuditionService = Depends(Provide[Container.audition_service]),
):
    auditons = await audition_service.get_auditions()

    return V1HttpResponse(content=auditons)


@router.post(
    path="/{round_id}/apply",
    response_model=BaseHttpResponse[ApplyProfile],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def user_apply_for_round(
    round_id: int,
    profile: ApplyProfile,
    auth: str = Cookie(None),
    audition_service: AuditionService = Depends(Provide[Container.audition_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user = await user_service.verify_token(auth)
    message = await audition_service.apply_for_round(user.id, round_id, profile)

    return V1HttpResponse(content="")


@router.get(
    path="/apply/list",
    response_model=BaseHttpResponse[str],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def user_apply_list(
    auth: str = Cookie(None),
    audition_service: AuditionService = Depends(Provide[Container.audition_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user = await user_service.verify_token(auth)
    message = await audition_service.get_audition_round_join_apply_list(user.id)

    return V1HttpResponse(content=message)
