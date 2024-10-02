from app.db.repositories.payment_repository import PaymentRepository
from app.clients.paypal_client import PayPalClient
import app.db.schemas.payment as schemas
from fastapi import HTTPException
from app.db.transactional import Transactional


class PaymentService:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        paypal_client: PayPalClient,
    ):
        self.payment_repository = payment_repository
        self.paypal_client = paypal_client

    @Transactional()
    async def _create_payment(self, payment_data: schemas.PaymentCreate):
        payment = await self.payment_repository.create_payment(payment_data)
        print("CHECK PONINT 01")
        payment_req = await schemas.Payment.from_dict(payment)
        return payment_req
