from fastapi import status
from app.exceptions.base_exception import AppException

class OtpExpiredException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired", error_code="OTP_EXPIRED")

class InvalidOtpException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP is invalid or expired", error_code="INVALID_OTP")

class OtpNotFoundException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="OTP not found", error_code="OTP_NOT_FOUND")