from typing import Optional
from datetime import datetime
from app.models.user import User, ApplicationForm
from pydantic.dataclasses import dataclass


@dataclass
class UserCreateReq:
    email: str
    name: str
    password: str
    channel: str
    # auth: str #관리자, 학생, 선생


@dataclass
class UserLoginReq:
    email: str
    password: str


@dataclass
class UserResp:
    id: int
    name: str
    email: str
    user_auth: str
    is_active: bool
    channel: str
    email_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_dto(cls, admin: User) -> "UserResp":
        return UserResp(
            id=admin.id,
            created_at=admin.created_at,
            updated_at=admin.updated_at,
            name=admin.name,
            email=admin.email,
            user_auth=admin.user_auth,
            is_active=admin.is_active,
            email_verified=admin.email_verified,
            channel=admin.channel,
        )


@dataclass
class VerifyCodeInput:
    email: str
    code: str


@dataclass
class Profile:
    date_of_birth: str
    phone: str
    school: str
    grade: str
    gender: str
    nationality: str
    height: str
    weight: str

    @classmethod
    def from_dto(cls, profile: ApplicationForm) -> "Profile":
        return Profile(
            id=profile.id,
            user_id=profile.user_id,
            date_of_birth=profile.date_of_birth,
            phone=profile.phone,
            school=profile.school,
            grade=profile.grade,
            gender=profile.gender,
            nationality=profile.nationality,
            height=profile.height,
            weight=profile.weight,
        )


@dataclass
class ApplyProfile:
    date_of_birth: str
    phone: str
    school: str
    grade: str
    gender: str
    nationality: str
    height: str
    weight: str
    category: str
