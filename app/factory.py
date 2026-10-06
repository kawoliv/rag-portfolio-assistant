"""Monta o pipeline com as implementações reais a partir da configuração."""

from __future__ import annotations

from .config import Settings
from .embeddings import SentenceTransformerEmbedder
from .llm import LLM, ClaudeLLM, OllamaLLM
from .rag import RAG
from .store import VectorStore


def construir_llm(settings: Settings) -> LLM:
    if settings.llm_provider == "ollama":
        return OllamaLLM(settings.ollama_model, settings.ollama_url, settings.max_tokens, settings.llm_timeout)
    if settings.llm_provider == "claude":
        return ClaudeLLM(settings.claude_model, settings.max_tokens)
    raise ValueError(f"LLM_PROVIDER inválido: {settings.llm_provider!r}. Use 'ollama' ou 'claude'.")


def construir_rag(settings: Settings) -> RAG:
    return RAG(
        store=VectorStore(settings.db_path),
        embedder=SentenceTransformerEmbedder(settings.embedding_model),
        llm=construir_llm(settings),
        top_k=settings.top_k,
        min_score=settings.min_score,
        chunk_chars=settings.chunk_chars,
        chunk_overlap=settings.chunk_overlap,
    )
