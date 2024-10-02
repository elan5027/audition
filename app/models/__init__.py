# 각 모델 파일을 임포트하여 베이스 메타데이터에 등록
from app.models.user import User, ApplicationForm
from app.models.course import Applicant, Audition, AuditionRound
from app.models.payment import Payment, Order

# 모든 모델을 포함한 베이스 모듈
__all__ = [
    "User",
    "Audition",
    "Applicant",
    "AuditionRound",
    "Payment",
    "Order",
    "ApplicationForm",
]
