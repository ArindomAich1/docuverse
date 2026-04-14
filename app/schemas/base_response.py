from typing import Optional
from typing import Any
from app.schemas.base_schema import BaseSchema

class BaseResponse(BaseSchema):
    data: Optional[Any] = None
    message: str