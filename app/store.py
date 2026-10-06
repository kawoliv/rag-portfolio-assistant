"""Armazenamento de documentos, trechos e vetores em SQLite.

Os vetores ficam numa coluna BLOB (float32). A busca carrega os vetores e calcula a
similaridade com NumPy: simples, sem servidor e rápido o bastante para alguns milhares
de trechos. Para volumes maiores, o próximo passo natural é pgvector ou um banco vetorial.
"""

from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .chunking import Chunk

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documentos (
    id         INTEGER PRIMARY KEY,
    caminho    TEXT NOT NULL UNIQUE,
    hash       TEXT NOT NULL,
    indexado_em TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS trechos (
    id           INTEGER PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos(id) ON DELETE CASCADE,
    ordem        INTEGER NOT NULL,
    titulo       TEXT NOT NULL,
    texto        TEXT NOT NULL,
    vetor        BLOB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_trechos_documento ON trechos(documento_id);
"""


@dataclass(frozen=True)
class Resultado:
    documento: str
    titulo: str
    texto: str
    score: float


class VectorStore:
    def __init__(self, caminho: Path | str) -> None:
        if str(caminho) != ":memory:":
            Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(caminho), check_same_thread=False)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SCHEMA)
        self._lock = threading.Lock()

    def hash_do_documento(self, caminho: str) -> str | None:
        with self._lock:
            linha = self._conn.execute(
                "SELECT hash FROM documentos WHERE caminho = ?", (caminho,)
            ).fetchone()
        return linha[0] if linha else None

    def salvar_documento(
        self, caminho: str, hash_: str, trechos: list[Chunk], vetores: np.ndarray
    ) -> None:
        if len(trechos) != len(vetores):
            raise ValueError("cada trecho precisa de exatamente um vetor")
        with self._lock, self._conn:
            self._conn.execute("DELETE FROM documentos WHERE caminho = ?", (caminho,))
            cur = self._conn.execute(
                "INSERT INTO documentos (caminho, hash) VALUES (?, ?)", (caminho, hash_)
            )
            doc_id = cur.lastrowid
            self._conn.executemany(
                "INSERT INTO trechos (documento_id, ordem, titulo, texto, vetor)"
                " VALUES (?, ?, ?, ?, ?)",
                [
                    (doc_id, i, t.titulo, t.texto, np.asarray(v, dtype=np.float32).tobytes())
                    for i, (t, v) in enumerate(zip(trechos, vetores))
                ],
            )

    def remover_ausentes(self, caminhos_existentes: set[str]) -> list[str]:
        with self._lock, self._conn:
            todos = [c for (c,) in self._conn.execute("SELECT caminho FROM documentos")]
            removidos = [c for c in todos if c not in caminhos_existentes]
            self._conn.executemany(
                "DELETE FROM documentos WHERE caminho = ?", [(c,) for c in removidos]
            )
        return removidos

    def buscar(self, vetor_consulta: np.ndarray, k: int) -> list[Resultado]:
        with self._lock:
            linhas = self._conn.execute(
                "SELECT d.caminho, t.titulo, t.texto, t.vetor"
                " FROM trechos t JOIN documentos d ON d.id = t.documento_id"
            ).fetchall()
        if not linhas:
            return []
        matriz = np.stack([np.frombuffer(l[3], dtype=np.float32) for l in linhas])
        scores = matriz @ np.asarray(vetor_consulta, dtype=np.float32)
        melhores = np.argsort(-scores)[:k]
        return [
            Resultado(linhas[i][0], linhas[i][1], linhas[i][2], float(scores[i]))
            for i in melhores
        ]

    def listar_documentos(self) -> list[dict]:
        with self._lock:
            linhas = self._conn.execute(
                "SELECT d.caminho, d.indexado_em, COUNT(t.id)"
                " FROM documentos d LEFT JOIN trechos t ON t.documento_id = d.id"
                " GROUP BY d.id ORDER BY d.caminho"
            ).fetchall()
        return [{"documento": c, "indexado_em": e, "trechos": n} for c, e, n in linhas]

    def contar_trechos(self) -> int:
        with self._lock:
            return int(self._conn.execute("SELECT COUNT(*) FROM trechos").fetchone()[0])
