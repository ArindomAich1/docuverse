from app.enums.user_types import UserType
from pydantic import EmailStr
from app.schemas.base_schema import BaseSchema

class UserRegistationRequest(BaseSchema):
    email: EmailStr
    name: str
    password: str

class UserResponse(BaseSchema):
    id: int
    name: str
    email: EmailStr
    user_type: UserType
    status_id: int

class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str

class UserLoginRequest(BaseSchema):
    email: EmailStr
    password: str
