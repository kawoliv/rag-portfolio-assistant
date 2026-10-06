from fastapi.testclient import TestClient

from app.api import criar_app
from app.config import Settings
from app.llm import ErroLLM


def _cliente(rag, docs):
    return TestClient(criar_app(rag=rag, settings=Settings(docs_dir=docs)))


def test_fluxo_completo_indexar_e_perguntar(rag, docs):
    with _cliente(rag, docs) as c:
        assert c.post("/indexar").json()["trechos"] > 0
        assert c.get("/saude").json()["status"] == "ok"
        r = c.post("/perguntar", json={"pergunta": "Como funciona o pagamento em duas formas?"})
        assert r.status_code == 200
        corpo = r.json()
        assert corpo["encontrou"] is True
        assert corpo["fontes"][0]["documento"] == "caixa.md"


def test_pergunta_curta_demais_retorna_422(rag, docs):
    with _cliente(rag, docs) as c:
        assert c.post("/perguntar", json={"pergunta": "oi"}).status_code == 422


def test_falha_do_modelo_vira_502(rag, docs, llm):
    def falhar(*_):
        raise ErroLLM("limite de uso atingido")

    llm.responder = falhar
    with _cliente(rag, docs) as c:
        c.post("/indexar")
        r = c.post("/perguntar", json={"pergunta": "Como funciona o pagamento em duas formas?"})
        assert r.status_code == 502
        assert "limite de uso" in r.json()["detail"]


def test_pagina_de_demonstracao_e_servida(rag, docs):
    with _cliente(rag, docs) as c:
        r = c.get("/")
        assert r.status_code == 200 and "Pergunte sobre os projetos" in r.text
