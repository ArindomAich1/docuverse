from pydantic import BaseModel

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        validate_assignment=True