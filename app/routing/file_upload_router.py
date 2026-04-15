from app.services.file_service import FileService
from fastapi import APIRouter, Depends, UploadFile, File
from app.api.dependency import get_access_token_user_id
from app.utils.s3_utils import upload_file, get_presigned_url
from app.schemas.base_response import BaseResponse
from app.exceptions.s3_exceptions import (
    FileTypeNotAllowedException,
    FileSizeExceededException,
    FileUploadFailedException,
    FileNotFoundException
)

router = APIRouter(prefix="/upload")

@router.post("/", response_model=BaseResponse, tags=["Upload"])
def upload(
    file: UploadFile = File(...),
    folder: str = "upload",
    user_id: int = Depends(get_access_token_user_id)
):
    service = FileService()
    return service.upload(file, f"{folder}/{user_id}")

@router.get("/presigned-url", response_model=BaseResponse, tags=["Upload"])
def presigned_url(
    s3_key: str,
    user_id: int = Depends(get_access_token_user_id)
):
    service = FileService()
    return service.presigned_url(s3_key)