"""API REST do assistente.

Rotas:
  GET  /            página simples para testar no navegador
  GET  /saude       status e quantidade de trechos indexados
  GET  /documentos  documentos indexados
  POST /indexar     (re)indexa a pasta de documentos; só processa o que mudou
  POST /perguntar   responde uma pergunta com citações das fontes
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .config import Settings
from .llm import ErroLLM
from .rag import RAG

STATIC = Path(__file__).parent / "static"


class PerguntaIn(BaseModel):
    pergunta: str = Field(min_length=3, max_length=500, examples=["Como funciona o pagamento dividido?"])
    k: int | None = Field(default=None, ge=1, le=10, description="Quantos trechos recuperar")


class FonteOut(BaseModel):
    n: int
    documento: str
    secao: str
    trecho: str
    score: float


class RespostaOut(BaseModel):
    resposta: str
    encontrou: bool = Field(description="Se havia trechos relevantes para responder")
    fontes: list[FonteOut]


class IndexacaoOut(BaseModel):
    indexados: list[str]
    inalterados: list[str]
    removidos: list[str]
    trechos: int


def criar_app(rag: RAG | None = None, settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    estado: dict[str, RAG | None] = {"rag": rag}

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if estado["rag"] is None:
            from .factory import construir_rag

            estado["rag"] = construir_rag(settings)
        yield

    app = FastAPI(
        title="RAG de projetos",
        description="Perguntas e respostas sobre documentação técnica, com citação das fontes.",
        version="1.0.0",
        lifespan=lifespan,
    )

    def pipeline() -> RAG:
        if estado["rag"] is None:
            raise HTTPException(503, "O pipeline ainda está carregando.")
        return estado["rag"]

    @app.get("/", include_in_schema=False)
    def pagina() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    @app.get("/saude")
    def saude() -> dict:
        return {"status": "ok", "trechos": pipeline().store.contar_trechos()}

    @app.get("/documentos")
    def documentos() -> list[dict]:
        return pipeline().store.listar_documentos()

    @app.post("/indexar", response_model=IndexacaoOut)
    def indexar() -> IndexacaoOut:
        try:
            relatorio = pipeline().indexar_pasta(settings.docs_dir)
        except FileNotFoundError as erro:
            raise HTTPException(404, str(erro)) from erro
        return IndexacaoOut(**relatorio.__dict__)

    @app.post("/perguntar", response_model=RespostaOut)
    def perguntar(entrada: PerguntaIn) -> RespostaOut:
        try:
            resposta = pipeline().perguntar(entrada.pergunta, entrada.k)
        except ValueError as erro:
            raise HTTPException(422, str(erro)) from erro
        except ErroLLM as erro:
            raise HTTPException(502, str(erro)) from erro
        return RespostaOut(**resposta.para_dict())

    return app


app = criar_app()
