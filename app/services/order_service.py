from fastapi import HTTPException, BackgroundTasks
from typing import Optional, List
from app.db.repositories.order_repository import OrderRepository
import app.models.payment as models
from app.db.session import session
from uuid import uuid4
from app.db.transactional import Transactional


class OrderService:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def generate_hashed_uuid(self, product_type: str, length=16):
        try:
            unique_id = f"{product_type}-{uuid4().hex[:length]}"

            # 중복된 invite_code가 있으면 새로운 것을 생성
            while await self.order_repository.retrieve_class_by_invite_code(unique_id):
                unique_id = f"{product_type}-{uuid4().hex[:length]}"

            return unique_id

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate unique ID for product type {product_type}: {str(e)}",
            )

    @Transactional()
    async def create_order(self, order: models.Order, user_id: int):
        try:
            return await self.order_repository.create_order(order, user_id)

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to create order for user ID {user_id}: {str(e)}",
            )

    @Transactional()
    async def _update_order_status(self, order_id: int, user_id: int, status: str):
        try:
            await self.order_repository.update_order_status(order_id, user_id, status)

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to update order status for order ID {order_id} and user ID {user_id}: {str(e)}",
            )

    async def get_order_by_order_id_and_user_id(self, order_id: int, user_id: int):
        try:
            order = await self.order_repository.get_order_by_order_id_and_user_id(
                order_id, user_id
            )
            if not order:
                raise HTTPException(
                    status_code=404,
                    detail=f"Order not found for order ID {order_id} and user ID {user_id}",
                )
            return order
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching order with order ID {order_id} and user ID {user_id}: {str(e)}",
            )

    async def _get_order_by_order_order_id_and_user_id(
        self, order_id: str, user_id: int
    ) -> models.Order:
        # try:
        order = await self.order_repository.get_order_by_order_order_id_and_user_id(
            order_id, user_id
        )
        if not order:
            raise HTTPException(
                status_code=404,
                detail=f"Order with order ID {order_id} not found for user ID {user_id}",
            )
        return order
        # except Exception as e:
        #     raise HTTPException(
        #         status_code=500,
        #         detail=f"Error retrieving order with order ID {order_id} for user ID {user_id}: {str(e)}",
        #     )
