from app.exceptions.s3_exceptions import FileNotFoundException
from app.utils.s3_utils import get_presigned_url
from app.exceptions.s3_exceptions import FileUploadFailedException
from app.exceptions.s3_exceptions import FileSizeExceededException
from app.exceptions.s3_exceptions import FileTypeNotAllowedException
from app.schemas.base_response import BaseResponse
from app.utils.s3_utils import upload_file
from fastapi import UploadFile

class FileService:
    def __init__(self):
        pass

    def upload(self, file: UploadFile, folder: str = "uploads"):
        try:
            s3_key = upload_file(file, folder=folder)
            return BaseResponse(
                data={"s3_key": s3_key},
                message="File uploaded successfully"
            )
        except ValueError as e:
            if "type" in str(e):
                raise FileTypeNotAllowedException()
            raise FileSizeExceededException()
        except Exception:
            raise FileUploadFailedException()

    def presigned_url(self, s3_key: str):
        try:
            url = get_presigned_url(s3_key)
            return BaseResponse(
                data={"url": url},
                message="Presigned URL generated successfully"
            )
        except ValueError:
            raise FileNotFoundException()
        except Exception:
            raise FileUploadFailedException()
