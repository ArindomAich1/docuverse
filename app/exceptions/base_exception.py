from fastapi import HTTPException

class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code = status_code, detail=detail)
        self.error_code = error_code