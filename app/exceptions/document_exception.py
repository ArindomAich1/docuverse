from app.exceptions.base_exception import AppException
from fastapi import status

class MaxDocumentUploadCountExexption(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Max document upload count reached", error_code="MAX_DOCUMENT_UPLOAD_REACHED")
