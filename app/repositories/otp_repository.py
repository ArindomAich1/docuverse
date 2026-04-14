from typing import List
from app.enums.otp_operation_type import OtpOperationType
from app.models.otp_model import OTP
from app.enums.row_status import RowStatus
from sqlalchemy.orm import Session

class OtpRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, otp: OTP) -> OTP:
        self.db.add(otp)
        self.db.flush()
        self.db.refresh(otp)
        return otp
    
    def save_all(self, otp_list: List[OTP]) -> List[OTP]:
        self.db.add_all(otp_list)
        self.db.flush()
        for otp in otp_list:
            self.db.refresh(otp)
        return otp_list

    def get_otp(self, user_id: int, operation_type: OtpOperationType, status = RowStatus):
        result = self.db.query(OTP).filter(
            OTP.user_id == user_id,
            OTP.operation_type == operation_type.value,
            OTP.status_id == status.value
        ).first()
        print(f"Repository returning: {result}")
        return result


