"""Geração de embeddings.

`SentenceTransformerEmbedder` roda um modelo multilíngue localmente (sem custo de API).
`HashEmbedder` é determinístico e leve, usado nos testes para não baixar modelos.
Os dois devolvem vetores normalizados, então similaridade de cosseno = produto escalar.
"""

from __future__ import annotations

import hashlib
import re
from typing import Protocol

import numpy as np


class Embedder(Protocol):
    dimensao: int

    def embed_documentos(self, textos: list[str]) -> np.ndarray: ...

    def embed_consulta(self, texto: str) -> np.ndarray: ...


def _normalizar(matriz: np.ndarray) -> np.ndarray:
    normas = np.linalg.norm(matriz, axis=1, keepdims=True)
    normas[normas == 0] = 1.0
    return (matriz / normas).astype(np.float32)


class SentenceTransformerEmbedder:
    def __init__(self, modelo: str) -> None:
        from sentence_transformers import SentenceTransformer  # import pesado, só quando usado

        self._modelo = SentenceTransformer(modelo)
        self.dimensao = int(self._modelo.get_sentence_embedding_dimension())

    def embed_documentos(self, textos: list[str]) -> np.ndarray:
        if not textos:
            return np.zeros((0, self.dimensao), dtype=np.float32)
        vetores = self._modelo.encode(textos, batch_size=32, show_progress_bar=False)
        return _normalizar(np.asarray(vetores, dtype=np.float32))

    def embed_consulta(self, texto: str) -> np.ndarray:
        return self.embed_documentos([texto])[0]


class HashEmbedder:
    """Saco de palavras com hashing: palavras em comum geram vetores parecidos."""

    def __init__(self, dimensao: int = 512) -> None:
        self.dimensao = dimensao

    def _vetor(self, texto: str) -> np.ndarray:
        v = np.zeros(self.dimensao, dtype=np.float32)
        for palavra in re.findall(r"\w+", texto.lower()):
            if len(palavra) < 3:
                continue
            h = int(hashlib.md5(palavra.encode()).hexdigest(), 16)
            v[h % self.dimensao] += 1.0
        return v

    def embed_documentos(self, textos: list[str]) -> np.ndarray:
        if not textos:
            return np.zeros((0, self.dimensao), dtype=np.float32)
        return _normalizar(np.stack([self._vetor(t) for t in textos]))

    def embed_consulta(self, texto: str) -> np.ndarray:
        return self.embed_documentos([texto])[0]
