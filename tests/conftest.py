import pytest

from app.embeddings import HashEmbedder
from app.llm import FakeLLM
from app.rag import RAG
from app.store import VectorStore


@pytest.fixture
def docs(tmp_path):
    pasta = tmp_path / "docs"
    pasta.mkdir()
    (pasta / "caixa.md").write_text(
        "# Sistema de caixa\n\nPDV para lanchonete.\n\n"
        "## Pagamento dividido\n\nUma venda pode ser paga em duas formas, como dinheiro e cartão. "
        "A soma das duas precisa bater com o total da venda.\n\n"
        "## Fechamento\n\nNo fechamento o sistema gera uma planilha Excel com quatro abas.\n",
        encoding="utf-8",
    )
    (pasta / "filmes.md").write_text(
        "# MatchMovie\n\n## Busca\n\nA busca de filmes usa debounce de 500 ms para evitar "
        "uma requisição por tecla digitada.\n",
        encoding="utf-8",
    )
    return pasta


@pytest.fixture
def llm():
    return FakeLLM("A venda pode ser paga em duas formas [1].")


@pytest.fixture
def rag(llm):
    return RAG(VectorStore(":memory:"), HashEmbedder(), llm, top_k=3, min_score=0.15)
