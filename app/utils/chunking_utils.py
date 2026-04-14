from app.schemas.chunk_schemas import ParentChunk, SubChunk
from dataclasses import dataclass
from typing import List, Tuple
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config.config import settings

def _clean_for_child(text: str) -> str:
    """Light cleaning only for child chunks."""
    # Remove non-printable/control chars except newline and tab
    text = re.sub(r'[^\x20-\x7E\n\t]', ' ', text)
    # Collapse 3+ newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Collapse multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    # Fix hyphenation at line breaks: "compensa-\ntion" -> "compensation"
    text = re.sub(r'-\n', '', text)

    return text.strip()


def build_splitters():
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.PARENT_CHUNK_SIZE,
        chunk_overlap=0,
        separators=["\n\n", "\n", "."],      # structural only
    )
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHILD_CHUNK_SIZE,
        chunk_overlap=settings.CHILD_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],  # can split anywhere
    )
    return parent_splitter, child_splitter


_PARENT_SPLITTER, _CHILD_SPLITTER = build_splitters()


def chunk_text(raw_text: str) -> Tuple[List[ParentChunk], List[SubChunk]]:
    """
    Parents: raw text from PDF splitter (no cleaning).
    Children: cleaned text derived from each parent.
    """
    # 1) Parents from ORIGINAL text
    parent_docs = _PARENT_SPLITTER.create_documents([raw_text])

    parent_chunks: List[ParentChunk] = []
    sub_chunks: List[SubChunk] = []
    sub_index = 0

    for p_index, parent_doc in enumerate(parent_docs):
        # store parent EXACTLY as split from raw_text
        parent_chunks.append(
            ParentChunk(
                text=parent_doc.page_content,
                parent_index=p_index,
            )
        )

        # 2) Children from CLEANED parent text
        cleaned_parent = _clean_for_child(parent_doc.page_content)

        child_docs = _CHILD_SPLITTER.create_documents([cleaned_parent])
        for child_doc in child_docs:
            sub_chunks.append(
                SubChunk(
                    text=child_doc.page_content,
                    chunk_index=sub_index,
                    parent_index=p_index,
                )
            )
            sub_index += 1

    return parent_chunks, sub_chunks
