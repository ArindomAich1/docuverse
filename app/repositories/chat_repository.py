from app.enums.row_status import RowStatus
from sqlalchemy.orm import Session
from app.models.chat_model import Chats

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_last_n_pair(self, document_id: int, n: int) -> list[Chats]:
        return (
            self.db.query(Chats)
            .filter(
                Chats.document_id == document_id,
                Chats.status_id == RowStatus.ACTIVE.value
            )
            .order_by(Chats.created_at.desc())
            .limit(n * 2)
            .all()[::-1]        # reverse to get chronological order
        )


    def save(self, chat: Chats) -> Chats:
        self.db.add(chat)
        self.db.flush()
        self.db.refresh(chat)
        return chat