from typing import Optional, List
from datetime import datetime
from pydantic.dataclasses import dataclass
from app.models.payment import Order as OrderModel
from app.models.payment import Payment as PaymentModel


@dataclass
class PaymentReq:
    order_id: str
    payment_key: str
    amount: str


@dataclass
class PaymentBase:
    order_id: str
    payment_id: str
    amount: float
    currency: str
    method: str
    payment_status: str
    payment_date: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    receipt_url: Optional[str] = None


@dataclass
class PaymentCreate(PaymentBase):
    pass


@dataclass
class Payment(PaymentBase):
    id: int = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None

    @classmethod
    async def from_dict(cls, payment_data: PaymentModel) -> "Payment":
        return cls(
            id=payment_data.id,
            order_id=payment_data.order_id,
            payment_id=payment_data.payment_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            method=payment_data.method,
            payment_status=payment_data.payment_status,
            payment_date=payment_data.payment_date,
            approved_at=payment_data.approved_at,
            receipt_url=payment_data.receipt_url,
            created_at=payment_data.created_at,
            updated_at=payment_data.updated_at,
        )


# Order 스키마
@dataclass
class OrderBase:
    order_id: str
    order_amount: float
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    order_name: Optional[str] = None
    currency: Optional[str] = None
    order_status: Optional[str] = "pending"


@dataclass
class OrderCreate(OrderBase):
    pass


@dataclass
class OrderCreateReq:
    product_type: str
    product_id: int


@dataclass
class Order(OrderBase):
    id: int = None
    created_at: datetime = None
    updated_at: datetime = None

    @classmethod
    def from_dto(cls, order: OrderModel) -> "OrderModel":

        return Order(
            order_id=order.order_id,
            order_amount=order.order_amount,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            order_name=order.order_name,
            currency=order.currency,
            order_status=order.order_status,
        )
