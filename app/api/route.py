from fastapi import APIRouter
from app.api.v1 import user, aws, payment, order, audition

router = APIRouter()

router.include_router(user.router, tags=["User"], prefix="/user")
router.include_router(aws.router, tags=["AWS"], prefix="/aws")
router.include_router(payment.router, tags=["PAYMENT"], prefix="/payments")
router.include_router(order.router, tags=["ORDER"], prefix="/order")
router.include_router(audition.router, tags=["AUDITION"], prefix="/audition")
