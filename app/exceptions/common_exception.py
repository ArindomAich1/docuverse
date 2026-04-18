from app.exceptions.base_exception import AppException
from fastapi import status

class InvalidRequestException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request", error="INVALID_REQUEST")

class InvalidFileTypeException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request", error="INVALID_FILE_TYPE")

class ChatLockedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Another device is currently accessing this chat. Please wait and try again.",
            error="CHAT_LOCKED"
        )