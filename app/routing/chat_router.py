from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.dependency import get_access_token_user_id
from app.schemas.chat_schemas import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/{document_id}/stream")
def stream_chat(
    document_id: int,
    request: ChatRequest,
    user_id: int = Depends(get_access_token_user_id),
    db: Session = Depends(get_db)
):
    service = ChatService(db)
    return StreamingResponse(
        service.stream_answer(
            document_id=document_id,
            user_id=user_id,
            query=request.content
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"   # disables Nginx response buffering
        }
    )


@router.get("/{document_id}/history")
def get_history(
    document_id: int,
    n: int = 10,
    user_id: int = Depends(get_access_token_user_id),
    db: Session = Depends(get_db)
):
    service = ChatService(db)
    return service.get_history(document_id, n)