from app.exceptions.base_exception import AppException
from fastapi import status

class UserNotFoundException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found", error_code="USER_NOT_FOUND")

class UserAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists with the same email", error_code="USER_ALREADY_EXISTS")

class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", error_code="INVALID_CREDENTIALS")

class UserNotActiveException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active", error_code="USER_NOT_ACTIVE")

class UnauthorizedException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token", error_code="UNAUTHORIZED")