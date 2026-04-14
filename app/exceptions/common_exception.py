from app.exceptions.base_exception import AppException
from fastapi import status

class InvalidRequestException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request", error="INVALID_REQUEST")

class InvalidFileTypeException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request", error="INVALID_FILE_TYPE")
