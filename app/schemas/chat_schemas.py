from app.enums.chat_roles import ChatRoles
from app.schemas.base_schema import BaseSchema

class ChatRequest(BaseSchema):
    content: str

class ChatHistoryItem(BaseSchema):
    id: int
    role: ChatRoles
    content: str