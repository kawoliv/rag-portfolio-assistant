"""Pipeline RAG: indexa documentos e responde perguntas com base neles."""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .chunking import dividir_markdown
from .embeddings import Embedder
from .llm import LLM
from .prompts import NAO_ENCONTRADO, SISTEMA, montar_mensagem
from .store import VectorStore

EXTENSOES = (".md", ".txt")
_CITACAO = re.compile(r"\[(\d+)\]")


@dataclass
class Fonte:
    n: int
    documento: str
    secao: str
    trecho: str
    score: float


@dataclass
class Resposta:
    resposta: str
    encontrou: bool
    fontes: list[Fonte] = field(default_factory=list)

    def para_dict(self) -> dict:
        return asdict(self)


@dataclass
class RelatorioIndexacao:
    indexados: list[str] = field(default_factory=list)
    inalterados: list[str] = field(default_factory=list)
    removidos: list[str] = field(default_factory=list)
    trechos: int = 0


class RAG:
    def __init__(
        self,
        store: VectorStore,
        embedder: Embedder,
        llm: LLM,
        top_k: int = 4,
        min_score: float = 0.30,
        chunk_chars: int = 1200,
        chunk_overlap: int = 200,
    ) -> None:
        self.store = store
        self.embedder = embedder
        self.llm = llm
        self.top_k = top_k
        self.min_score = min_score
        self.chunk_chars = chunk_chars
        self.chunk_overlap = chunk_overlap

    # ---------- indexação ----------
    def indexar_pasta(self, pasta: Path | str) -> RelatorioIndexacao:
        pasta = Path(pasta)
        if not pasta.is_dir():
            raise FileNotFoundError(f"Pasta de documentos não encontrada: {pasta}")

        relatorio = RelatorioIndexacao()
        arquivos = sorted(p for p in pasta.rglob("*") if p.suffix.lower() in EXTENSOES)
        existentes: set[str] = set()

        for arquivo in arquivos:
            nome = arquivo.relative_to(pasta).as_posix()
            existentes.add(nome)
            texto = arquivo.read_text(encoding="utf-8")
            hash_ = hashlib.sha256(texto.encode("utf-8")).hexdigest()
            if self.store.hash_do_documento(nome) == hash_:
                relatorio.inalterados.append(nome)
                continue

            trechos = dividir_markdown(texto, nome, self.chunk_chars, self.chunk_overlap)
            # O título da seção entra no texto do embedding: ajuda a achar o trecho certo.
            vetores = self.embedder.embed_documentos([f"{t.titulo}\n{t.texto}" for t in trechos])
            self.store.salvar_documento(nome, hash_, trechos, vetores)
            relatorio.indexados.append(nome)
            relatorio.trechos += len(trechos)

        relatorio.removidos = self.store.remover_ausentes(existentes)
        return relatorio

    # ---------- perguntas ----------
    def recuperar(self, pergunta: str, k: int | None = None):
        vetor = self.embedder.embed_consulta(pergunta)
        return self.store.buscar(vetor, k or self.top_k)

    def perguntar(self, pergunta: str, k: int | None = None) -> Resposta:
        pergunta = pergunta.strip()
        if not pergunta:
            raise ValueError("A pergunta não pode ficar vazia.")

        relevantes = [r for r in self.recuperar(pergunta, k) if r.score >= self.min_score]
        if not relevantes:
            # Sem contexto suficiente, nem chama o modelo: evita custo e resposta inventada.
            return Resposta(resposta=NAO_ENCONTRADO, encontrou=False)

        texto = self.llm.responder(SISTEMA, montar_mensagem(pergunta, relevantes))

        citados = {int(n) for n in _CITACAO.findall(texto)}
        fontes = [
            Fonte(i, r.documento, r.titulo, r.texto, round(r.score, 4))
            for i, r in enumerate(relevantes, start=1)
            if not citados or i in citados
        ]
        return Resposta(resposta=texto, encontrou=True, fontes=fontes)
