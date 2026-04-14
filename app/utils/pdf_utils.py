import requests
import fitz
import pymupdf4llm
import os
import re
from app.utils.chunking_utils import chunk_text

def pdf_to_txt(url: str):
    response = requests.get(url)
    response.raise_for_status()

    with fitz.open(stream=response.content, filetype="pdf") as doc:
        md_text = pymupdf4llm.to_markdown(doc) 

    cleaned = clean_markdown(md_text)

    print(f"Extraction successful!")
    
    return cleaned

def clean_markdown(text: str) -> str:
    # remove bold markers **
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    
    # remove heading markers ##
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # remove extra blank lines (more than 2 in a row)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # remove trailing spaces on each line
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    
    return text.strip()

if __name__ == "__main__":

    text = pdf_to_txt("https://docuverse-s3.s3.amazonaws.com/upload/1/test_table_234a2d04-3470-4c30-8b8a-3cfc297ea0d9.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA4MTWNT2PT5E2QSAV%2F20260324%2Fap-south-1%2Fs3%2Faws4_request&X-Amz-Date=20260324T205752Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=878200da94a24ae487c50fe19ac5ed5b25f34facf40bc1d7aac8d3a434e978bd")
    output_path = "/home/user2a/Desktop/Projects/test_docuverse/sample3.txt"

    parent_chunks, sub_chunks = chunk_text(text)

    text = text + "\n\n---\n\n" + str(parent_chunks) + "\n\n---\n\n" + str(sub_chunks)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
