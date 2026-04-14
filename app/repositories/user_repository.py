from app.enums.row_status import RowStatus
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.models.user_model import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: EmailStr, status_id: int):
        result = self.db.query(User).filter(
            User.email == email,
            User.status_id == status_id
        ).first()
        return result
    
    def get_by_id(self, id: int, status_id: int):
        result = self.db.query(User).filter(
            User.id == id,
            User.status_id == status_id
        ).first()
        print(f"Repository returning: {result}")
        return result
    
    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user