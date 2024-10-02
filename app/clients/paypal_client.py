import base64
import app.db.schemas.payment as schemas
import aiohttp
from fastapi import HTTPException


class PayPalClient:
    def __init__(self, payment_key: str) -> None:
        self._app_key = base64.b64encode((payment_key + ":").encode("utf-8")).decode(
            "utf-8"
        )
        self._headers = {
            "Authorization": f"Basic {self._app_key}",
            "Content-Type": "application/json",
        }

    async def payment_complate(self, payment: schemas.PaymentReq):
        print("TEST : ", self._headers)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url="https://api.tosspayments.com/v1/payments/confirm",
                headers=self._headers,
                json={
                    "orderId": payment.order_id,
                    "paymentKey": payment.payment_key,
                    "amount": payment.amount,
                },
            ) as response:
                if response.status != 200:
                    print("!!DQWDQD : ", await response.json())
                    raise HTTPException(status_code=400, detail="Payment Error")
                
                result = await response.json()

        return result
