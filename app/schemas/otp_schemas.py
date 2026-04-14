from app.enums.otp_operation_type import OtpOperationType
from pydantic import EmailStr
from app.schemas.base_schema import BaseSchema

class OtpGenerateRequest(BaseSchema):
    email: EmailStr
    operation_type: OtpOperationType


class OtpVerifyRequest(BaseSchema):
    email: EmailStr
    operation_type: OtpOperationType
    otp: str

