from fastapi import status
from app.exceptions.base_exception import AppException

class FileTypeNotAllowedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed",
            error_code="FILE_TYPE_NOT_ALLOWED"
        )

class FileSizeExceededException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit",
            error_code="FILE_SIZE_EXCEEDED"
        )

class FileUploadFailedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed",
            error_code="FILE_UPLOAD_FAILED"
        )

class FileNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
            error_code="FILE_NOT_FOUND"
        )