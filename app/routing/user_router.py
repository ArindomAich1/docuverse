from app.schemas.user_schemas import UserLoginRequest
from app.api.dependency import get_access_token_user_id, get_refresh_token_user_id
from app.utils.jwt_utils import decode_token
from pydantic import EmailStr
from app.services.user_service import UserService
from sqlalchemy.orm import Session
from app.schemas.user_schemas import UserResponse, UserRegistationRequest
from app.schemas.base_response import BaseResponse
from app.db.database import get_db
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/user")

@router.get("/", response_model=UserResponse, tags=["User"])
def get_user(email: EmailStr, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_user_by_email(email)

@router.post("/register", response_model=BaseResponse, tags=["User"], status_code=status.HTTP_201_CREATED)
def register(request: UserRegistationRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.register(request)

@router.get("/profile", response_model=BaseResponse, tags=["User"])
def get_profile(db: Session = Depends(get_db), user_id = Depends(get_access_token_user_id)):
    service = UserService(db)
    return service.get_profile(user_id)

@router.post("/login", response_model=BaseResponse, tags=["User"])
def login(request: UserLoginRequest,db: Session = Depends(get_db)):
    service = UserService(db)
    return service.login(request)

@router.post("/refresh", response_model=BaseResponse, tags=["User"])
def refresh(db: Session = Depends(get_db), user_id = Depends(get_refresh_token_user_id)):
    service = UserService(db)
    return service.refresh(user_id)