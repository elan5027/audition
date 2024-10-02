from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Table,
    DateTime,
    Boolean,
    Text,
    Numeric,
)
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.sql import func


class Audition(Base):
    __tablename__ = "auditions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, index=True, unique=True)
    thumbnail_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Text)  # 활성화, 비활성화,
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # 관계 설정: 오디션 종류 관계
    rounds = relationship(
        "AuditionRound", back_populates="audition", cascade="all, delete"
    )


class AuditionRound(Base):
    __tablename__ = "audition_rounds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # 1차, 2차, 3차
    audition_id = Column(Integer, ForeignKey("auditions.id", ondelete="CASCADE"))
    price = Column(Numeric(10, 5), nullable=False)  # 각 라운드별 지원비용
    thumbnail_url = Column(Text, nullable=True)
    reviewer = Column(Text, nullable=False)
    start_at = Column(DateTime(timezone=True), nullable=False)  # 지원 시작 시기
    end_at = Column(DateTime(timezone=True), nullable=False)  # 지원 마감 시기
    result_at = Column(DateTime(timezone=True), nullable=False)  # 평가 결과 시기
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계 설정: 오디션 라운드가 속한 오디션
    audition = relationship("Audition", back_populates="rounds")

    # 오디션 라운드에 지원한 지원자 목록
    applicants = relationship("Applicant", back_populates="audition_round")


class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    round_id = Column(
        Integer, ForeignKey("audition_rounds.id", ondelete="CASCADE"), index=True
    )

    # 사용자 지원서 정보
    date_of_birth = Column(String)
    phone = Column(String)
    school = Column(String)
    grade = Column(String)
    gender = Column(String)
    nationality = Column(String)
    height = Column(String)
    weight = Column(String)

    # 오디션 지원 종류( 춤, 노래 분류 ),
    category = Column(String)
    # video_url = Column(String, nullable=True)  # 지원자가 제출한 영상의 URL
    # image_dir_url = Column(String, nullable=True)

    passed = Column(String, default="PENDING")  # 해당 라운드 통과 여부
    payment = Column(Boolean, default=False)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 설정: 지원한 유저
    user = relationship("User", back_populates="auditions", cascade="all, delete")

    # 관계 설정: 지원한 오디션 라운드
    audition_round = relationship(
        "AuditionRound", back_populates="applicants", cascade="all, delete"
    )

    def __repr__(self):
        return f"<Applicant(id={self.id}, user_id={self.user_id}, round_id={self.round_id}, passed={self.passed})>"
