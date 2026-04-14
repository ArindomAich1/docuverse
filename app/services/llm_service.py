# app/services/llm_service.py

import json
import time
import requests
from typing import Generator
from app.config.config import settings


# =============================================================================
# MODELS — right-sized per task
# =============================================================================
EXPANSION_MODEL  = "meta/llama-3.1-8b-instruct"
GENERATION_MODEL = "mistralai/mistral-large-3-675b-instruct-2512"
EMBEDDING_MODEL  = "nvidia/llama-3.2-nv-embedqa-1b-v2"

NVIDIA_CHAT_URL      = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_EMBEDDING_URL = "https://integrate.api.nvidia.com/v1/embeddings"


# =============================================================================
# PROMPTS
# =============================================================================
QUERY_EXPANSION_SYSTEM_PROMPT = """You are a query expansion assistant for a document retrieval system.
Users upload various types of personal documents such as contracts, agreements, letters, reports, invoices, and official correspondence.

Your job is to rewrite the user's query into an expanded search query that improves retrieval accuracy.

Rules:
- Identify and resolve any abbreviations or domain-specific shorthand present in the query
- Add relevant synonyms and semantically related terms
- Keep the expanded query concise — no more than 15 words
- Return ONLY the expanded query string, nothing else
- No explanations, no bullet points, no formatting

Examples:
User: What is the payment amount?
Output: payment amount total cost price fee charge sum due invoice

User: When does the agreement expire?
Output: agreement expiry expiration end date termination validity period contract

User: What are the penalties?
Output: penalty clause fine charge consequence breach violation liability damages

User: Who are the parties involved?
Output: parties involved names signatories individuals organizations entities agreement"""


ANSWER_GENERATION_SYSTEM_PROMPT = """You are a precise document assistant. Answer the user's question using ONLY the context provided.

Rules:
- Base your answer strictly on the provided context — do not use external knowledge
- If the answer is not found in the context, respond with: "I could not find this information in the document."
- Be concise and direct — avoid unnecessary filler or repetition
- If the answer contains numbers, dates, or names, quote them exactly as they appear in the context
- Do not make assumptions or inferences beyond what is explicitly stated"""


# =============================================================================
# INTERNALS
# =============================================================================
def _get_headers(stream: bool) -> dict:
    return {
        "Authorization": f"Bearer {settings.NVDIA_API}",
        "Accept": "text/event-stream" if stream else "application/json"
    }


def _post_with_retry(
    url: str,
    headers: dict,
    payload: dict,
    stream: bool = False,
    max_retries: int = 3
) -> requests.Response:
    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, json=payload, stream=stream)
        if response.status_code == 429:
            time.sleep(2 ** attempt)   # 1s → 2s → 4s
            continue
        response.raise_for_status()
        return response
    raise RuntimeError("NVIDIA API rate limit exceeded after retries")


# =============================================================================
# SERVICE
# =============================================================================
class LLMService:

    # -------------------------------------------------------------------------
    # Query Expansion — REST, short output, deterministic
    # -------------------------------------------------------------------------
    def expand_query(self, query: str) -> str:
        payload = {
            "model": EXPANSION_MODEL,
            "messages": [
                {"role": "system", "content": QUERY_EXPANSION_SYSTEM_PROMPT},
                {"role": "user",   "content": query}
            ],
            "max_tokens": 50,
            "temperature": 0.0,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stream": False
        }
        response = _post_with_retry(NVIDIA_CHAT_URL, _get_headers(stream=False), payload)
        return response.json()["choices"][0]["message"]["content"].strip()

    # -------------------------------------------------------------------------
    # Embedding — for both document ingestion and query vectorization
    # -------------------------------------------------------------------------
    def embed(self, texts: list[str], input_type: str = "query") -> list[list[float]]:
        """
        input_type: "query" for search queries | "passage" for document chunks
        """
        payload = {
            "model": EMBEDDING_MODEL,
            "input": texts,
            "input_type": input_type,
            "encoding_format": "float"
        }
        response = _post_with_retry(NVIDIA_EMBEDDING_URL, _get_headers(stream=False), payload)
        return [item["embedding"] for item in response.json()["data"]]

    # -------------------------------------------------------------------------
    # Answer Generation — REST (full response, use for background tasks / tests)
    # -------------------------------------------------------------------------
    def generate_answer(self, query: str, context_chunks: list[str]) -> str:
        context = "\n\n---\n\n".join(context_chunks)
        payload = {
            "model": GENERATION_MODEL,
            "messages": [
                {"role": "system", "content": ANSWER_GENERATION_SYSTEM_PROMPT},
                {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ],
            "max_tokens": 2048,
            "temperature": 0.15,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stream": False
        }
        response = _post_with_retry(NVIDIA_CHAT_URL, _get_headers(stream=False), payload)
        return response.json()["choices"][0]["message"]["content"].strip()

    # -------------------------------------------------------------------------
    # Answer Generation — Stream (token by token, use for frontend chat UX)
    # -------------------------------------------------------------------------
    def generate_answer_stream(
        self,
        query: str,
        context_chunks: list[str]
    ) -> Generator[str, None, None]:
        context = "\n\n---\n\n".join(context_chunks)
        payload = {
            "model": GENERATION_MODEL,
            "messages": [
                {"role": "system", "content": ANSWER_GENERATION_SYSTEM_PROMPT},
                {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ],
            "max_tokens": 2048,
            "temperature": 0.15,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stream": True
        }
        response = _post_with_retry(
            NVIDIA_CHAT_URL,
            _get_headers(stream=True),
            payload,
            stream=True
        )

        for line in response.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                data = decoded[len("data: "):]
                if data.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    choices = chunk.get("choices", [])
                    if not choices:
                        continue
                    delta = choices[0]["delta"].get("content", "")
                    if delta:
                        yield delta
                except (json.JSONDecodeError, KeyError):
                    continue