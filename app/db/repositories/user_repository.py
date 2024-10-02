from typing import List, Optional
from app.models.user import User, ApplicationForm
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import session
from fastapi import HTTPException


class UserRepository:

    async def find_by_user_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def find_by_manager_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def find_by_user_auth(self, user_auth: str) -> List[User]:
        stmt = select(User).where(User.user_auth == user_auth)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def find_by_user_name(self, user_name: str):
        stmt = select(User).where(User.name == user_name)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def delete_by_user_email(self, user_email: str) -> None:
        stmt = delete(User).where(User.email == user_email)
        await session.execute(stmt)
        await session.commit()

    async def find_all_user(self) -> List[User]:
        stmt = select(User)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def _verify_email(self, user_id: int) -> str:
        user = await self.find_by_user_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        if user.email_verified:
            return "이미 이메일이 인증되었습니다."

        user.email_verified = True
        user.is_active = True

        session.add(user)
        await session.commit()

        return "이메일 인증이 완료되었습니다."

    async def create_user(self, user: User):
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def create_profile(self, profile: ApplicationForm):
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile

    async def find_by_user_id_from_profile(self, user_id: int) -> ApplicationForm:
        stmt = select(ApplicationForm).where(ApplicationForm.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()
