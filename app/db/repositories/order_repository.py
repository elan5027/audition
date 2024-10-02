import app.db.schemas.payment as schemas
import app.models.payment as models
from datetime import datetime, timezone
from app.db.session import session
from sqlalchemy.future import select
from sqlalchemy import delete


class OrderRepository:
    async def create_order(self, order: schemas.OrderCreate, user_id: int):
        db_order = models.Order(
            order_id=order.order_id,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            order_name=order.order_name,
            order_amount=order.order_amount,
            currency=order.currency,
            order_status=order.order_status,
            user_id=user_id,
        )
        session.add(db_order)
        await session.commit()
        await session.refresh(db_order)

        return db_order

    # 주문 조회
    async def get_order_by_order_id_and_user_id(
        self, order_id: int, user_id: int
    ) -> models.Order:
        stmt = select(models.Order).where(
            models.Order.id == order_id, models.Order.user_id == user_id
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_order_by_order_order_id_and_user_id(
        self, order_id: str, user_id: int
    ) -> models.Order:
        stmt = select(models.Order).where(
            models.Order.order_id == order_id, models.Order.user_id == user_id
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    # 주문 상태 업데이트
    async def update_order_status(
        self, order_id: int, user_id: int, status: str
    ) -> models.Order:
        db_order = await self.get_order_by_order_id_and_user_id(order_id, user_id)

        if db_order:
            db_order.order_status = status
            db_order.updated_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(db_order)
        return db_order

    async def retrieve_class_by_invite_code(self, order_id: str):
        stmt = select(models.Order).where(models.Order.order_id == order_id)
        result = await session.execute(stmt)
        data = result.scalar_one_or_none()
        if data:
            return schemas.Order(id=data.id)
        else:
            return None
