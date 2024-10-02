from fastapi import APIRouter, Request, Depends, HTTPException, Cookie
import app.db.schemas.payment as schemas
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.core.containers import Container
from app.services.user_service import UserService
from app.services.audition_service import AuditionService
from dependency_injector.wiring import Provide, inject
from datetime import datetime, timezone
from asyncio import gather as asyncio_gather


from app.db.schemas.common import (
    BaseHttpResponse,
    V1HttpResponse,
    ErrorResponse,
    Paging,
)

router = APIRouter()


# 결제에 대한 CURD 로직
@router.post(
    path="/complete",
    response_model=BaseHttpResponse[schemas.Payment],
    responses={400: {"model": ErrorResponse}},
)
@inject
async def payments_complete(
    payment: schemas.PaymentReq,
    payment_service: PaymentService = Depends(Provide[Container.payment_service]),
    order_service: OrderService = Depends(Provide[Container.order_service]),
    audition_service: AuditionService = Depends(Provide[Container.audition_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
    auth: str = Cookie(None),
):
    user = await user_service.verify_token(auth)

    # 주문 정보 조회
    response = await payment_service.paypal_client.payment_complate(payment)
    if response:
        # 결제조회 : paymentKey, orderId
        # 결제취소 : paymentKey
        receipt = response.get("receipt")
        receipt_url = receipt.get("url") if receipt else None
        payment_date = response.get("requestedAt")
        approved_at = response.get("approvedAt", None)

        payment_date = datetime.strptime(
            payment_date, "%Y-%m-%dT%H:%M:%S%z"
        ).astimezone(timezone.utc)
        approved_at = (
            datetime.strptime(approved_at, "%Y-%m-%dT%H:%M:%S%z").astimezone(
                timezone.utc
            )
            if approved_at
            else None
        )

        order_id = response.get("orderId")

        # # 결제 정보 생성 또는 업데이트
        payment_data = schemas.PaymentCreate(
            payment_id=response.get("paymentKey"),
            order_id=order_id,
            amount=response.get("totalAmount"),
            currency=response.get("currency"),
            method=response.get("method"),  # DONE, PENDING, CANCELED
            payment_status=response.get("status"),
            payment_date=payment_date,  # 요청 시간
            approved_at=approved_at,  # 결제 시간 (옵션: 없을 수 있음)
            receipt_url=receipt_url,  # 영수증 URL이 없을 경우 None 처리
        )
        payment = await payment_service._create_payment(payment_data)
        order = await order_service._get_order_by_order_order_id_and_user_id(
            order_id, user.id
        )
        # payment, order = await asyncio_gather(
        #     payment_service._create_payment(payment_data),
        #     order_service._get_order_by_order_order_id_and_user_id(order_id, user.id),
        # )
        print("CHECKS : ", order.order_name)
        audition = await audition_service._get_audition_round_by_order_name_to_model(  # 얘가 None으로 반환됨.
            order.order_name
        )
        print("CHECK", audition.id)
        await audition_service._update_applicant_payment_status(user.id, audition.id),
        await order_service._update_order_status(order.id, user.id, "DONE"),

        # await asyncio_gather(
        #     audition_service._update_applicant_payment_status(user.id, audition.id),
        #     order_service._update_order_status(order.id, user.id, "DONE"),
        # )

        return V1HttpResponse(
            content=payment,
        )

    else:
        raise HTTPException(status_code=400, detail="Payments complate fail.")


@router.post("/cancel")
async def cancel_payment(request: Request):
    pass


# 결제조회
@router.post("/serch")
async def portone_webhook(request: Request):
    pass


# 모든 결제 테이블 받아오기

# 유저의 결제 테이블 받아오기

# 해당 오더의 결제 테이블 받아오기

# 해당 제품의 모든 결제 테이블 받아오기(필터 고려, 결제 상태에 대한)
