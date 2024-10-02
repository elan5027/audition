from fastapi import HTTPException, BackgroundTasks
from typing import Optional, List
from app.models.user import User, ApplicationForm
from app.db.schemas.user import UserResp, UserCreateReq, VerifyCodeInput, Profile
from app.services.encryption import SeedCbcCipher
from app.db.repositories.user_repository import UserRepository
import base64
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# from app.clients.smtp_client import SMTPClient
from app.db.transactional import Transactional
import os

SECRET_KEY = os.getenv("SECRET_KEY", "Null")  # 기본값 설정
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        # smtp_client: SMTPClient,
        key: str,
        iv: str,
    ) -> None:
        self.user_repository = user_repository
        # self.smtp_client = smtp_client
        self.encryption = SeedCbcCipher(
            key=base64.b64decode(key), iv=iv.encode("utf-8")
        )
        self.pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

    def _decode_and_decrypt(self, encoded_str: str) -> str:
        if len(encoded_str) % 4 != 0:
            encoded_str += "=" * (4 - len(encoded_str) % 4)
        decoded_str = base64.b64decode(encoded_str)
        dcrypt = self.encryption.decrypt(decoded_str)
        return dcrypt.decode("utf-8")

    async def get_user_data(self, user) -> UserResp:
        if isinstance(user, (int, str)):
            user = await self.user_repository.find_by_user_id(user)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
        print(user)
        user_schema = UserResp.from_dto(user)
        # try:
        #     user_schema.email = self._decode_and_decrypt(user_schema.email)
        # except Exception as e:
        #     raise HTTPException(status_code=500, detail=f"Error decoding or decrypting email: {str(e)}")

        return user_schema

    async def get_user_profile(self, user_id):
        profile = await self.user_repository.find_by_user_id_from_profile(user_id)

        if not profile:
            return False
        _profile = Profile.from_dto(profile)
        return _profile

    @Transactional()
    async def create_user_profile(self, user_id, profile: Profile):
        is_profile = await self.user_repository.find_by_user_id_from_profile(user_id)

        if is_profile:
            raise HTTPException(status_code=400, detail="User alrady profile")

        _profile = ApplicationForm(
            user_id=user_id,
            date_of_birth=profile.date_of_birth,
            phone=profile.phone,
            school=profile.school,
            grade=profile.grade,
            gender=profile.gender,
            nationality=profile.nationality,
            height=profile.height,
            weight=profile.weight,
        )
        add_profile = await self.user_repository.create_profile(_profile)
        return add_profile

    @Transactional()
    async def update_user_profile(self, user_id, profile: Profile):
        existing_profile = await self.user_repository.find_by_user_id_from_profile(
            user_id
        )

        if not existing_profile:
            raise HTTPException(
                status_code=404, detail="Profile not found for the given user"
            )

        existing_profile.date_of_birth = (
            profile.date_of_birth
            if profile.date_of_birth
            else existing_profile.date_of_birth
        )
        existing_profile.phone = (
            profile.phone if profile.phone else existing_profile.phone
        )
        existing_profile.school = (
            profile.school if profile.school else existing_profile.school
        )
        existing_profile.grade = (
            profile.grade if profile.grade else existing_profile.grade
        )
        existing_profile.gender = (
            profile.gender if profile.gender else existing_profile.gender
        )
        existing_profile.nationality = (
            profile.nationality if profile.nationality else existing_profile.nationality
        )
        existing_profile.height = (
            profile.height if profile.height else existing_profile.height
        )
        existing_profile.weight = (
            profile.weight if profile.weight else existing_profile.weight
        )

        add_profile = await self.user_repository.create_profile(existing_profile)
        return add_profile

    async def get_users_data(self) -> List[UserResp]:
        users = await self.user_repository.find_all_user()
        user_schemas = []
        if users:
            for user in users:
                user_schema = UserResp.from_dto(user)
                try:
                    # _email = self._decode_and_decrypt(user_schema.email)
                    # _phone_number = self._decode_and_decrypt(user_schema.phone_number)
                    # user_schema.email = _email
                    # user_schema.phone_number = _phone_number
                    user_schemas.append(user_schema)
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error decoding or decrypting email: {str(e)}",
                    )
            return user_schemas
        else:
            raise HTTPException(status_code=404, detail="User not found")

    @Transactional()
    async def add_user(self, user: UserCreateReq) -> User:
        existing_user = await self.user_repository.find_by_manager_email(user.email)
        print(existing_user)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="User with this identification already exists."
            )

        # enc_manager_email = base64.b64encode(self.encryption.encrypt(user.email.encode('utf-8'))).decode('utf-8')
        # enc_phone_number = base64.b64encode(self.encryption.encrypt(user.phone_number.encode('utf-8'))).decode('utf-8')
        _user = User(
            password=self.pwd_context.hash(user.password),
            name=user.name,
            email=user.email,
            # user_auth = self._map_user_auth(user.auth),
            updated_at=datetime.now(tz=timezone.utc),
            channel=user.channel,
            user_auth="Student",
            is_active=True,
            email_verified=True,
        )
        return await self.user_repository.create_user(user=_user)

    # 권한 필요시 요건에 맞게 수정
    def _map_user_auth(self, auth: str) -> str:
        if auth == "관리자":
            return "Role_Admin"
        elif auth == "학생회원":
            return "Role_Student"
        elif auth == "선생회원":
            return "Role_Teacher"
        return auth

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def verify_token(self, token: str) -> UserResp:
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            if not token:
                raise credentials_exception
            _token = token.replace("Bearer ", "")
            payload = jwt.decode(_token, SECRET_KEY, algorithms=[ALGORITHM])
            admin_id: str = payload.get("sub", "")
            if not admin_id:
                raise credentials_exception
            return await self.get_user_data(int(admin_id))
        except JWTError:
            raise credentials_exception

    def _encode_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def login_user(self, username: str, password: str) -> str:
        user = await self.user_repository.find_by_manager_email(username)
        if not user or not self.pwd_context.verify(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        return access_token
