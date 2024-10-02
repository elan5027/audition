from fastapi import HTTPException, BackgroundTasks
from typing import Optional, List
from app.models.course import AuditionRound, Audition, Applicant
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.audition_repository import AuditionRepository
from app.db.schemas.course import AuditionResp, RoundResp, AuditionRoundApplyResp
from app.db.schemas.user import ApplyProfile
import base64
from datetime import datetime, timezone, timedelta
from app.db.session import session
from app.db.transactional import Transactional


class AuditionService:
    def __init__(self, audition_repository: AuditionRepository):
        self.audition_repository = audition_repository

    @Transactional()
    async def create_auditions(self, audition_data: AuditionResp):
        audition = await self.audition_repository.create_audition(audition_data)
        auditions = AuditionResp.from_dict(audition)
        return auditions

    @Transactional()
    async def apply_for_round(self, user_id: int, round_id: int, profile: ApplyProfile):
        # 지원할 오디션 존재 여부 확인
        round_info = await self.audition_repository.find_rounds_by_round_id(round_id)
        if not round_info:
            raise HTTPException(
                status_code=400, detail="This is an audition that doesn't exist."
            )

        # 검증 이미 지원햇는지 여부 확인
        is_apply = await self.audition_repository.find_apply_by_round_id(
            user_id, round_id
        )
        if is_apply:
            raise HTTPException(
                status_code=400, detail="This audition has already been completed."
            )

        now = datetime.now(timezone.utc)

        # 지원 가능한 시기인지 확인
        if not (round_info.start_at <= now <= round_info.end_at):
            raise HTTPException(
                status_code=400, detail="This is not the time to apply."
            )

        apply = await self.audition_repository.create_apply(
            user_id=user_id, round_id=round_id, profile=profile
        )

        return apply

    @Transactional()
    async def _update_applicant_payment_status(self, user_id: int, audition_id: int):
        await self.audition_repository.update_applicant_payment_status(
            user_id, audition_id
        )

    async def get_auditions(self):
        auditions = await self.audition_repository.find_by_audition_all()
        audition_list = [AuditionResp.from_dict(audition) for audition in auditions]
        return audition_list

    async def get_audition_round(self, round_id: int) -> RoundResp:
        round = await self.audition_repository.find_rounds_by_round_id(round_id)
        round_req = RoundResp.from_dict(round)  # 수정하기
        return round_req

    async def get_audition_round_join_apply_list(self, user_id: int) -> RoundResp:
        try:
            rounds = await self.audition_repository.find_round_join_apply_by_all(
                user_id
            )
            round_join_apply = [
                AuditionRoundApplyResp.from_dict(round) for round in rounds
            ]
            return round_join_apply
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to fetch audition rounds: {str(e)}."
            )

    async def get_apply(self, user_id: int) -> RoundResp:
        rounds = await self.audition_repository.find_round_join_apply_by_all(user_id)
        round_join_apply = [AuditionRoundApplyResp.from_dict(round) for round in rounds]
        return round_join_apply

    async def _get_audition_round_by_order_name_to_model(
        self, order_name: str
    ) -> AuditionRound:
        round = await self.audition_repository.get_audition_round_by_order_name(
            order_name
        )
        return round
