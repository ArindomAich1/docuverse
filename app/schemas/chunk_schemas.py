from dataclasses import dataclass

@dataclass(frozen=True)
class ParentChunk:
    text: str
    parent_index: int

@dataclass(frozen=True)
class SubChunk:
    text: str
    chunk_index: int
    parent_index: int