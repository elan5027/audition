from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime
from sqlalchemy.sql import func


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)  # 주문 고유 ID
    order_id = Column(
        String(255), unique=True, index=True, nullable=False
    )  # 주문 ID   #Input
    customer_name = Column(
        String(255)
    )  # 고객 이름 # token검증 & 유저 Input -> 옵셔널 None일경우 유저 email
    customer_email = Column(
        String(255)
    )  # 고객 이메일 # token검증 & 유저 Input -> 옵셔널 None일경우 유저 email
    order_name = Column(String(255))  # 주문 상품명 # Order serch
    order_amount = Column(DECIMAL(10, 2), nullable=False)  # 주문 금액 # Order serch
    currency = Column(String(10))  # 통화 (예: KRW, USD) #USD 고정? 지워도 될려나
    order_status = Column(
        String(50), default="pending"
    )  # 주문 상태 # 기본 PENDING 에서 PASS
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user_id = Column(
        Integer, ForeignKey("user.id"), nullable=False
    )  # 주문한 사용자와의 연관
    user = relationship(
        "User", back_populates="orders"
    )  # 사용자 정보와 연관된 관계 설정

    # 결제 정보와의 관계


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)  # 결제 고유 ID
    payment_id = Column(
        String(255), index=True, nullable=False
    )  # 결제 ID  -> 인풋 결제키
    order_id = Column(String(255), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)  # 결제 금액 -> 오더금액
    currency = Column(String(10))  # 통화 (예: KRW, USD) -> 오더 USD
    method = Column(String(50))  # 결제 수단 (예: 카드, 가상계좌) -> 결제정보
    payment_status = Column(String(50))  # 결제 상태 -> 결제정보
    payment_date = Column(DateTime(timezone=True))  # 결제 완료 시각
    approved_at = Column(DateTime(timezone=True))  # 결제 승인 시각
    receipt_url = Column(String(255), nullable=True)  # 영수증 URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    # 주문 정보와의 관계
