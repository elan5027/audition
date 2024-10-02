from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey
from app.models.base import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    password = Column(String)
    name = Column(String)
    email = Column(String, unique=True)
    user_auth = Column(String, nullable=True)  # 선생, 학생, 관리자
    is_active = Column(Boolean, default=False)  # 비활성화, 미인증, 인증완료
    email_verified = Column(Boolean, default=False)
    channel = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    orders = relationship(
        "Order", back_populates="user", cascade="all, delete"
    )  # 사용자가 생성한 주문 목록
    auditions = relationship("Applicant", back_populates="user", cascade="all, delete")
    application_form = relationship(
        "ApplicationForm", back_populates="user", uselist=False, cascade="all, delete"
    )


class ApplicationForm(Base):
    __tablename__ = "application_form"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True
    )  # User 테이블의 id와 1:1 관계
    date_of_birth = Column(String)
    phone = Column(String)
    school = Column(String)
    grade = Column(String)
    gender = Column(String)
    nationality = Column(String)
    height = Column(String)
    weight = Column(String)

    # User와의 관계 설정
    user = relationship("User", back_populates="application_form")
