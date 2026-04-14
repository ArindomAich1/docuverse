from app.schemas.base_schema import BaseSchema

class UploadDocRequest(BaseSchema):
    document_path: str