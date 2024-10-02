from typing import List, Optional
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from app.models.course import Audition, AuditionRound
from datetime import datetime


@dataclass
class AWSReq:
    file_name: str
    directory: str


@dataclass
class RoundResp:
    name: str
    price: float
    thumbnail_url: str
    reviewer: str
    start_at: datetime
    end_at: datetime
    result_at: datetime

    @classmethod
    def from_dict(cls, round_data: AuditionRound) -> "RoundResp":
        return cls(
            name=round_data.name,
            price=round_data.price,
            thumbnail_url=round_data.thumbnail_url,
            reviewer=round_data.reviewer,
            start_at=round_data.start_at,
            end_at=round_data.end_at,
            result_at=round_data.result_at,
        )


@dataclass
class AuditionResp:
    name: str
    description: str
    thumbnail_url: str
    rounds: List[RoundResp]

    @classmethod
    def from_dict(cls, audition_data: Audition) -> "AuditionResp":
        rounds = [
            RoundResp.from_dict(round_data) for round_data in audition_data.rounds
        ]
        return cls(
            name=audition_data.name,  # Assuming Audition is a model and has attributes instead of dict access
            description=audition_data.description,
            thumbnail_url=audition_data.thumbnail_url,
            rounds=rounds,
        )


@dataclass
class AuditionRoundApplyResp:
    round_id: int
    payment: bool
    passed: str
    name: str
    price: float
    reviewer: str
    thumbnail_url: Optional[str]
    category: Optional[str]
    start_at: datetime
    end_at: datetime
    result_at: datetime

    @classmethod
    def from_dict(cls, applicant_data: dict) -> "AuditionRoundApplyResp":
        # Applicant 데이터에서 각 필드를 추출
        round_data = (
            applicant_data.audition_round
        )  # Applicant의 audition_round 관계 참조

        return cls(
            round_id=applicant_data.round_id,
            category=applicant_data.category,
            payment=applicant_data.payment,
            passed=applicant_data.passed,
            name=round_data.name,
            price=round_data.price,
            thumbnail_url=round_data.thumbnail_url,
            reviewer=round_data.reviewer,
            start_at=round_data.start_at,
            end_at=round_data.end_at,
            result_at=round_data.result_at,
        )
