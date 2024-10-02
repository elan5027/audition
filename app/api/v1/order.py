from fastapi import APIRouter, Request, Depends, HTTPException, Cookie
import app.models.payment as models
import app.db.schemas.payment as schemas
import app.db.repositories.payment_repository as crud
from app.services.audition_service import AuditionService
from app.services.order_service import OrderService
from app.core.containers import Container
from app.services.user_service import UserService
from dependency_injector.wiring import Provide, inject
import uuid
import hashlib

from app.db.schemas.common import (
    BaseHttpResponse,
    V1HttpResponse,
    ErrorResponse,
    Paging,
)


router = APIRouter()


# 주문에 대한 CURD 로직
@router.post(
    path="/create",
    response_model=BaseHttpResponse[schemas.Order],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def order_create(
    product_data: schemas.OrderCreateReq,
    auth: str = Cookie(None),
    audition_service: AuditionService = Depends(Provide[Container.audition_service]),
    order_service: OrderService = Depends(Provide[Container.order_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user = await user_service.verify_token(auth)
    # user = await user_service.get_user_data(1)
    print(product_data)
    if product_data.product_type == "audition":
        product = await audition_service.get_audition_round(product_data.product_id)
        order_id = await order_service.generate_hashed_uuid(product_data.product_type)

        order = schemas.OrderCreate(
            order_id=order_id,  # 생성 uuid
            customer_name=user.name,
            customer_email=user.email,
            order_name=product.name,
            order_amount=product.price,
            currency="USD",
        )
        order_req = await order_service.create_order(order, user_id=user.id)
        print(order_req)
        return V1HttpResponse(
            content=schemas.Order.from_dto(order_req),
        )


@router.get(
    path="/{order_id}",
    response_model=BaseHttpResponse[schemas.Order],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def order_detail(
    order_id: int,
    auth: str = Cookie(None),
    order_service: OrderService = Depends(Provide[Container.order_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user = await user_service.verify_token(auth)
    order = await order_service.get_order_by_order_id_and_user_id(
        order_id=order_id, user_id=user.id
    )

    return V1HttpResponse(
        content=schemas.Order.from_dto(order),
    )


# 유저의 모든 주문 받아오기

# 모든 유저의 주문 받아오기
