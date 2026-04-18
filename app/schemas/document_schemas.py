from app.schemas.base_schema import BaseSchema
from datetime import datetime

class UploadDocRequest(BaseSchema):
    document_path: str

class DocumentResponse(BaseSchema):
    id: int
    document_name: str
    document_s3path: str
    created_at: datetime