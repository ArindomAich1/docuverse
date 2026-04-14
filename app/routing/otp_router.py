from app.schemas.otp_schemas import OtpVerifyRequest
from app.schemas.otp_schemas import OtpGenerateRequest
from app.enums.otp_operation_type import OtpOperationType
from app.services.otp_service import OtpService
from app.db.database import get_db
from fastapi import Depends, status
from sqlalchemy.orm import Session
from app.schemas.base_response import BaseResponse
from fastapi import APIRouter

router = APIRouter(prefix="/otp")

@router.post("/request-otp", response_model=BaseResponse, tags=["OTP"], status_code=status.HTTP_201_CREATED)
def request_otp(request: OtpGenerateRequest, db: Session = Depends(get_db)):
    service = OtpService(db)
    return service.request_otp(request.email, request.operation_type)

@router.post("/verify", response_model=BaseResponse, tags=["OTP"])
def verify_otp(request: OtpVerifyRequest, db: Session = Depends(get_db)):
    service = OtpService(db)
    return service.verify_otp(request.email, request.operation_type, request.otp)