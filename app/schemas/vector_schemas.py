from app.schemas.base_schema import BaseSchema

class VectorMetadata(BaseSchema):
    document_id: int
    user_id: int
    chunk_index: int
    parent_index: int
    text: str


class PineconeVector(BaseSchema):
    id: str
    values: list[float]
    sparse_values: dict
    metadata: VectorMetadata

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "values": self.values,
            "sparse_values": self.sparse_values,
            "metadata": self.metadata.model_dump()   # Pydantic v2
        }