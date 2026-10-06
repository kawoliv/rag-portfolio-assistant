"""Configuração da aplicação, lida de variáveis de ambiente (ou de um arquivo .env)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    docs_dir: Path = Path("docs")
    db_path: Path = Path("data/rag.db")
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    llm_provider: str = "ollama"  # "ollama" (gratuito, local) ou "claude" (API paga)
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    claude_model: str = "claude-haiku-4-5"
    max_tokens: int = 800
    llm_timeout: float = 180.0
    top_k: int = 4
    min_score: float = 0.30
    chunk_chars: int = 1200
    chunk_overlap: int = 200

    @classmethod
    def from_env(cls) -> "Settings":
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:  # python-dotenv é opcional
            pass

        padrao = cls()
        return cls(
            docs_dir=Path(os.getenv("DOCS_DIR", padrao.docs_dir)),
            db_path=Path(os.getenv("DB_PATH", padrao.db_path)),
            embedding_model=os.getenv("EMBEDDING_MODEL", padrao.embedding_model),
            llm_provider=os.getenv("LLM_PROVIDER", padrao.llm_provider).strip().lower(),
            ollama_url=os.getenv("OLLAMA_URL", padrao.ollama_url).rstrip("/"),
            ollama_model=os.getenv("OLLAMA_MODEL", padrao.ollama_model),
            claude_model=os.getenv("CLAUDE_MODEL", padrao.claude_model),
            max_tokens=int(os.getenv("MAX_TOKENS", padrao.max_tokens)),
            llm_timeout=float(os.getenv("LLM_TIMEOUT", padrao.llm_timeout)),
            top_k=int(os.getenv("TOP_K", padrao.top_k)),
            min_score=float(os.getenv("MIN_SCORE", padrao.min_score)),
            chunk_chars=int(os.getenv("CHUNK_CHARS", padrao.chunk_chars)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", padrao.chunk_overlap)),
        )
