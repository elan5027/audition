import app.db.schemas.payment as schemas
import app.models.payment as models
from datetime import datetime, timezone
from app.db.session import session
from sqlalchemy.future import select
from sqlalchemy import delete


class PaymentRepository:
    async def create_payment(self, payment: schemas.PaymentCreate):
        async with session() as db_session:  # 세션을 컨텍스트에서 가져오기
            db_payment = models.Payment(
                payment_id=payment.payment_id,
                order_id=payment.order_id,
                amount=payment.amount,
                currency=payment.currency,
                method=payment.method,
                payment_status=payment.payment_status,
                payment_date=payment.payment_date,
                approved_at=payment.approved_at,
                receipt_url=payment.receipt_url,
                updated_at=datetime.now(timezone.utc),
            )
            db_session.add(db_payment)
            await db_session.commit()
            await db_session.refresh(db_payment)
            return db_payment

    async def update_payment(self, payment_id: str, approved_at: datetime = None):
        stmt = select(models.Payment).where(models.Payment.payment_id == payment_id)
        result = await session.execute(stmt)
        db_payment = result.scalars().first()
        if db_payment:
            if approved_at:
                db_payment.approved_at = approved_at
            db_payment.updated_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(db_payment)
        return db_payment

    # 결제 정보 조회
    async def get_payment_by_imp_uid(self, order_id: str):
        stmt = select(models.Payment).where(models.Payment.order_id == order_id)
        result = await session.execute(stmt)
        return result.scalars().first()
