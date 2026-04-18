from app.schemas.document_schemas import UploadDocRequest
from app.db.database import get_db
from app.services.document_service import DocumentService
from sqlalchemy.orm import Session
from app.schemas.base_response import BaseResponse
from app.api.dependency import get_access_token_user_id
from fastapi import Depends, APIRouter

router = APIRouter(prefix="/document")

@router.post("/", response_model=BaseResponse, tags=["Document"])
def upload_doc(
    request: UploadDocRequest, 
    user_id: int = Depends(get_access_token_user_id),
    db: Session = Depends(get_db)
):
    service = DocumentService(db)
    return service.upload_doc(user_id, request.document_path)

@router.get("/", response_model=BaseResponse, tags=["Document"])
def get_all_documents(
    user_id: int = Depends(get_access_token_user_id),
    db: Session = Depends(get_db)
):
    service = DocumentService(db)
    return service.get_all_documents(user_id)
