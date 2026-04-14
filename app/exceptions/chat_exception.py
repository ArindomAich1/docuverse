from app.exceptions.base_exception import AppException
from fastapi import status

class DocumentNotFoundException(AppException):
    def __init__(self):
        super().__init__(status_code= status.HTTP_404_NOT_FOUND, detail="Document not found", error="DOCUMENT_NOT_FOUND")
