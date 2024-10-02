import logging
from app.models.course import Audition, AuditionRound, Applicant
from app.db.schemas.course import AuditionResp, RoundResp
from app.db.schemas.user import ApplyProfile
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from app.db.session import session
from sqlalchemy.orm import joinedload
from sqlalchemy import update


class AuditionRepository:

    async def create_audition(self, audition_data: AuditionResp) -> Audition:
        # 비동기 세션 사용
        async with session() as db_session:  # 세션을 컨텍스트에서 가져오기
            async with db_session.begin():  # 트랜잭션을 명시적으로 관리
                db_audition = Audition(
                    name=audition_data.name,
                    description=audition_data.description,
                    thumbnail_url=audition_data.thumbnail_url,
                    status="ACTIVE",
                )
                db_session.add(db_audition)
                await db_session.flush()  # 세션을 비동기로 flush

                # 라운드를 생성하는 내부 메서드 호출
                await self._create_audition_rounds(
                    audition_data.rounds, db_audition.id, db_session
                )
            db_audition = await db_session.execute(
                select(Audition)
                .options(joinedload(Audition.rounds))
                .filter_by(id=db_audition.id)
            )
            db_audition = db_audition.scalar()
        return db_audition  # 트랜잭션이 자동으로 commit됨

    async def _create_audition_rounds(
        self, rounds_data: List[RoundResp], audition_id: int, db_session
    ):
        """
        주어진 라운드 데이터를 사용하여 오디션 라운드를 생성하는 내부 메서드.
        여러 라운드를 한번에 생성하고, 트랜잭션으로 처리.
        """
        for round_data in rounds_data:
            db_round = AuditionRound(
                name=round_data.name,
                price=round_data.price,
                reviewer=round_data.reviewer,
                thumbnail_url=round_data.thumbnail_url,
                start_at=round_data.start_at,
                end_at=round_data.end_at,
                result_at=round_data.result_at,
                audition_id=audition_id,  # 참조할 오디션 ID
            )
            db_session.add(db_round)

        await db_session.flush()  # 비동기로 세션을 flush

    async def find_by_audition_id(self, audition_id: int) -> Audition:
        stmt = select(Audition).where(Audition.id == audition_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def find_rounds_by_audition(self, audition_id: int) -> AuditionRound:
        stmt = select(AuditionRound).where(AuditionRound.audition_id == audition_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def find_rounds_by_round_id(self, round_id: int) -> AuditionRound:
        stmt = select(AuditionRound).where(AuditionRound.id == round_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def find_by_audition_all(self) -> Audition:
        stmt = select(Audition).options(selectinload(Audition.rounds))
        result = await session.execute(stmt)
        return result.scalars().all()

    async def find_apply_by_round_id(self, user_id: int, round_id: int) -> Applicant:
        stmt = select(Applicant).where(
            Applicant.user_id == user_id, Applicant.round_id == round_id
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    async def find_apply_by_all(self, user_id: int) -> Applicant:
        stmt = select(Applicant).where(Applicant.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def find_round_join_apply_by_all(self, user_id: int) -> Applicant:

        stmt = (
            select(Applicant)
            .options(
                joinedload(Applicant.audition_round),  # 오디션 라운드 관계를 미리 로드
            )
            .filter(Applicant.user_id == user_id)
        )

        result = await session.execute(stmt)
        applicant = result.scalars().all()

        return applicant

    async def create_apply(self, user_id: int, round_id: int, profile: ApplyProfile):

        applicant = Applicant(
            user_id=user_id,
            round_id=round_id,
            category=profile.category,
            date_of_birth=profile.date_of_birth,
            phone=profile.phone,
            school=profile.school,
            grade=profile.grade,
            gender=profile.gender,
            nationality=profile.nationality,
            height=profile.height,
            weight=profile.weight,
        )
        session.add(applicant)
        await session.commit()
        return applicant

    async def update_applicant_payment_status(
        self, user_id: int, round_id: int
    ) -> Applicant:
        # 지원자의 결제 상태 업데이트
        await session.execute(
            update(Applicant)
            .where(Applicant.user_id == user_id)
            .where(Applicant.round_id == round_id)
            .values(payment=True)
        )
        await session.commit()

    async def get_audition_round_by_order_name(self, order_name: str) -> AuditionRound:
        # 주문 상품명(order_name)으로 오디션 라운드 정보 조회
        result = await session.execute(
            select(AuditionRound).where(AuditionRound.name == order_name)
        )
        return result.scalars().first()
