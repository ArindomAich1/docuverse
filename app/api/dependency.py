from app.exceptions.user_exceptions import UnauthorizedException
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt_utils import decode_token
from app.enums.jwt_enums import TokenType

bearer_scheme = HTTPBearer()

def get_access_token_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> int:
    try:
        payload = decode_token(credentials.credentials, TokenType.ACCESS)
        return int(payload.get("sub"))
    except ValueError:
        raise UnauthorizedException()


def get_refresh_token_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> int:
    try:
        payload = decode_token(credentials.credentials, TokenType.REFRESH)
        return int(payload.get("sub"))
    except ValueError:
        raise UnauthorizedException()