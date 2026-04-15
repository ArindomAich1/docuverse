from app.exceptions.user_exceptions import InvalidCredentialsException
from app.exceptions.user_exceptions import UnauthorizedException
from app.exceptions.user_exceptions import UserNotFoundException
from app.exceptions.base_exception import AppException
from app.exceptions.user_exceptions import UserAlreadyExistsException
from app.exceptions.user_exceptions import UserNotActiveException
from app.utils.jwt_utils import create_refresh_token
from app.utils.jwt_utils import create_access_token
from app.schemas.user_schemas import TokenResponse
from app.utils.password_utils import verify_password
from app.schemas.user_schemas import UserLoginRequest
from app.schemas.base_response import BaseResponse
from datetime import datetime, timedelta
from app.enums.otp_operation_type import OtpOperationType
from app.utils.string_generation import generate_otp
from app.models.otp_model import OTP
from app.repositories.otp_repository import OtpRepository
from app.enums.user_types import UserType
from sqlalchemy.orm import Session
from app.schemas.user_schemas import UserResponse, UserRegistationRequest
from app.models.user_model import User
from app.enums.row_status import RowStatus
from pydantic import EmailStr
from app.repositories.user_repository import UserRepository 
from app.utils.password_utils import hash_password

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def get_user_by_email(self, email: EmailStr):
        user = self.user_repository.get_by_email(email, RowStatus.ACTIVE.value)

        if user is None:
            raise UserNotActiveException()

        return UserResponse.model_validate(user)

    def register(self, request: UserRegistationRequest):
        try:
            existing_user = self.user_repository.get_by_email(request.email, RowStatus.ACTIVE.value)

            if existing_user is not None:
                raise UserAlreadyExistsException()

            existing_user = self.user_repository.get_by_email(request.email, RowStatus.INACTIVE.value)
            if existing_user is not None:
                existing_user.status_id = RowStatus.DELETED.value
                existing_user.deleted_at = datetime.now()

                self.user_repository.save(existing_user)

            user = User(
                name = request.name,
                email = request.email,
                password_hash = hash_password(request.password),
                user_type = UserType.USER,
                status_id = RowStatus.INACTIVE.value
            )

            self.user_repository.save(user)

            self.db.commit()
            return BaseResponse(
                message="User registered successfully. Verify otp to activate the user"
            )
        except AppException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise e

    def get_profile(self, user_id: int):
        user = self.user_repository.get_by_id(user_id, RowStatus.ACTIVE.value)

        if user is None:
            raise UserNotFoundException()

        user_response = UserResponse.model_validate(user)
        response = BaseResponse(
            data = user_response,
            message = "User retrieved successfully."
        )

        return response

    def login(self, request: UserLoginRequest) -> BaseResponse:
        user = self.user_repository.get_by_email(request.email, RowStatus.ACTIVE.value)

        if (user is None) or (verify_password(request.password, user.password_hash) is False):
            raise InvalidCredentialsException()
        
        token_response = TokenResponse(
                        access_token = create_access_token(user.id),
                        refresh_token = create_refresh_token(user.id)
                    )

        response = BaseResponse(
            data = token_response,
            message = "User verified successfully"
        )

        return response

    def refresh(self, userId) -> BaseResponse:
        user = self.user_repository.get_by_id(userId, RowStatus.ACTIVE.value)

        if (user is None):
            raise UserNotFoundException()
        
        token_response = TokenResponse(
                        access_token = create_access_token(user.id),
                        refresh_token = create_refresh_token(user.id)
                    )

        response = BaseResponse(
            data = token_response,
            message = "Tokes refreshed successfully"
        )

        return response


        


