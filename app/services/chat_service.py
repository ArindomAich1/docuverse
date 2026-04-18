from typing import Generator
from sqlalchemy.orm import Session

from app.utils.redis_utils import acquire_chat_lock, release_chat_lock
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.repositories.chat_repository import ChatRepository
from app.models.chat_model import Chats
from app.enums.chat_roles import ChatRoles
import logging

logger = logging.getLogger(__name__)

class ChatService:

    def __init__(self, db: Session):
        self.db = db
        self.llm_service      = LLMService()
        self.retrieval_service = RetrievalService(db)
        self.chat_repository  = ChatRepository(db)

    def stream_answer(
        self,
        document_id: int,
        user_id: int,
        query: str
    ) -> Generator[str, None, None]:
        """
        Full pipeline as a streaming generator:
          1. Persist user message (flush)
          2. Expand query via LLM for better retrieval recall
          3. Hybrid retrieve + rerank → hydrated parent chunks
          4. Stream LLM answer token by token
          5. Persist assistant message (flush → commit)

        The DB commit is atomic — both user and assistant messages
        commit together only after the full response is accumulated.
        On any failure, both are rolled back.
        """
        full_response = ""
        lock_token = None

        lock_token = acquire_chat_lock(document_id)
        if not lock_token:
            yield "data: [LOCKED] Another device is currently accessing this chat. Please wait.\n\n"
            return

        try:
            # ── Step 1: Persist user message ──────────────────────────────
            user_message = Chats(
                document_id=document_id,
                role=ChatRoles.USER,
                content=query,
                created_by=user_id,
                updated_by=user_id
            )
            self.chat_repository.save(user_message)

            # ── Step 2: Expand query for retrieval ────────────────────────
            # Original query is shown to user / stored in DB.
            # Expanded query is only used for Pinecone hybrid search.
            expanded_query = self.llm_service.expand_query(query)

            # ── Step 3: Hybrid retrieve + rerank ─────────────────────────
            contexts = self.retrieval_service.get_context(
                query=expanded_query,
                user_id=user_id,
                document_id=document_id
            )

            if not contexts:
                no_context_msg = "I could not find relevant information in this document."
                yield f"data: {no_context_msg}\n\n"
                full_response = no_context_msg
            else:
                # ── Step 4: Stream answer ─────────────────────────────────
                context_chunks = [ctx.text for ctx in contexts]
                for token in self.llm_service.generate_answer_stream(query, context_chunks):
                    full_response += token
                    yield f"data: {token}\n\n"

            # ── Step 5: Persist assistant message + commit ────────────────
            assistant_message = Chats(
                document_id=document_id,
                role=ChatRoles.AI,
                content=full_response,
                created_by=user_id,
                updated_by=user_id
            )
            self.chat_repository.save(assistant_message)
            self.db.commit()

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error("stream_answer failed: %s", str(e), exc_info=True)
            self.db.rollback()
            yield f"data: [ERROR] {str(e)}\n\n"

        finally:
            if lock_token:
                release_chat_lock(document_id, lock_token)

    def get_history(
        self,
        document_id: int,
        n: int = 10
    ) -> list[Chats]:
        """Returns last n Q&A pairs in chronological order."""
        return self.chat_repository.get_last_n_pair(document_id, n)