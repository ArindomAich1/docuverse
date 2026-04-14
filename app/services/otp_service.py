from app.exceptions.otp_exception import InvalidOtpException
from app.exceptions.base_exception import AppException
from app.exceptions.common_exception import InvalidRequestException
from app.exceptions.user_exceptions import UserNotFoundException
from app.utils.jwt_utils import create_refresh_token
from app.utils.jwt_utils import create_access_token
from app.schemas.user_schemas import TokenResponse
from logging import log
from fastapi import HTTPException
from app.schemas.base_response import BaseResponse
from typing import List
from datetime import timedelta, datetime
from app.utils.string_generation import generate_otp
from app.models.otp_model import OTP
from app.enums.row_status import RowStatus
from pydantic import EmailStr
from app.repositories.user_repository import UserRepository
from app.enums.otp_operation_type import OtpOperationType
from app.repositories.otp_repository import OtpRepository
from sqlalchemy.orm import Session

class OtpService:
    def __init__(self, db: Session):
        self.db = db
        self.otp_repository = OtpRepository(db)
        self.user_repository = UserRepository(db)

    def request_otp(self, email: EmailStr, operation_type: OtpOperationType):
        try:
            match(operation_type):
                case OtpOperationType.REGISTRATION:
                    
                    user = self.user_repository.get_by_email(email, RowStatus.INACTIVE.value)
                    if user is None:
                        raise UserNotFoundException()
                    print("User : ", user.id)
                    existing_otp = self.otp_repository.get_otp(user_id=user.id, operation_type = operation_type, status=RowStatus.ACTIVE)
                    
                    otp_list : List[OTP]  = []
                    if existing_otp is not None:
                        existing_otp.status_id = RowStatus.DELETED.value
                        existing_otp.deleted_at = datetime.now()
                        otp_list.append(existing_otp)

                    otp = OTP(
                        user_id = user.id,
                        otp = generate_otp(),
                        expiration_time = datetime.now() + timedelta(minutes=10),
                        operation_type = OtpOperationType.REGISTRATION.value,
                        status_id = RowStatus.ACTIVE.value,
                        created_by = user.id,
                        updated_by = user.id
                    )
                    otp_list.append(otp)
                    self.otp_repository.save_all(otp_list) 

                    self.db.commit()
                    return BaseResponse(
                        message="Otp generated successfully."
                    ) 
                case _:
                    raise InvalidRequestException()
        except AppException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            print(e)
            raise e


    def verify_otp(self, email: EmailStr, operation_type: OtpOperationType, otp: str):
        try:
            match(operation_type):
                case OtpOperationType.REGISTRATION:
                    
                    user = self.user_repository.get_by_email(email, RowStatus.INACTIVE.value)
                    if user is None:
                        raise UserNotFoundException()
                    print("User : ", user.id)
                    existing_otp = self.otp_repository.get_otp(user_id=user.id, operation_type = operation_type, status=RowStatus.ACTIVE)

                    if not (existing_otp.otp == otp and existing_otp.expiration_time > datetime.now()) :
                        raise InvalidOtpException()
                    existing_otp.status_id = RowStatus.DELETED.value
                    existing_otp.deleted_at = datetime.now()
                    self.otp_repository.save(existing_otp)

                    user.status_id = RowStatus.ACTIVE.value
                    self.user_repository.save(user)

                    token_response = TokenResponse(
                        access_token = create_access_token(user.id),
                        refresh_token = create_refresh_token(user.id)
                    )

                    response = BaseResponse(
                        data = token_response,
                        message = "User verified successfully"
                    )

                    self.db.commit()
                    return response
        except AppException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            print(e)
            raise e
