from sqlalchemy.orm import Session
from app.services.embedding_service import EmbeddingService
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.models.document_chunk_model import DocumentChunk
from typing import List
from app.utils.chunking_utils import chunk_text
from app.schemas.base_response import BaseResponse
from app.exceptions.document_exception import MaxDocumentUploadCountExexption
from app.exceptions.base_exception import AppException
from app.exceptions.common_exception import InvalidFileTypeException
from app.repositories.document_repository import DocumentRepository
from app.utils.s3_utils import get_presigned_url
from app.utils.pdf_utils import pdf_to_txt
from app.models.document_model import Documents
from app.config.config import settings


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.document_repository = DocumentRepository(db)
        self.document_chunk_repository = DocumentChunkRepository(db)
        self.embedding_service = EmbeddingService()

    def upload_doc(self, user_id: int, document_path: str):
        try:
            file_extension = document_path.split(".")[-1]
            if file_extension != "pdf":
                raise InvalidFileTypeException()

            existing_doc_count = self.document_repository.get_count_by_user(user_id)
            if existing_doc_count >= settings.ALLOWED_DOCUMENT_COUNT:
                raise MaxDocumentUploadCountExexption()

            presigned_url = get_presigned_url(document_path)
            
            text = pdf_to_txt(presigned_url)

            # step 1 : store the documet
            document = Documents(
                user_id = user_id,
                document_s3path = document_path,
                document_name = document_path.split("/")[-1]
            )

            self.document_repository.save(document)

            # step 2 : chunk text 
            parent_chunks, sub_chunks = chunk_text(text)
            
            # step 3 : save parent chunk
            document_parent_chunks: List[DocumentChunk] = [
                        DocumentChunk(
                            document_id=document.id,
                            parent_index=parent_chunk.parent_index,
                            text=parent_chunk.text,
                            created_by=user_id,
                            updated_by=user_id
                        )
                        for parent_chunk in parent_chunks
                    ]
            self.document_chunk_repository.save_all(document_parent_chunks)
            
            # step 4 : generate embeddings and save child chunk
            self.embedding_service.upsert_chunks(
                document_id=document.id,
                user_id=user_id,
                chunks=sub_chunks
            )
            # setp 5 : 
            self.db.commit()
            return BaseResponse(
                data = {"document_id": document.id},
                message = "Document uploaded successfully"
            )
        except AppException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise e