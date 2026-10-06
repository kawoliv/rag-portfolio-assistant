import numpy as np

from app.chunking import Chunk
from app.embeddings import HashEmbedder
from app.store import VectorStore


def _salvar(store, emb, nome, textos, hash_="h1"):
    trechos = [Chunk(nome, t) for t in textos]
    store.salvar_documento(nome, hash_, trechos, emb.embed_documentos(textos))


def test_busca_retorna_o_trecho_mais_parecido_primeiro():
    store, emb = VectorStore(":memory:"), HashEmbedder()
    _salvar(store, emb, "a.md", ["fechamento do caixa gera planilha", "receita de bolo de cenoura"])
    resultados = store.buscar(emb.embed_consulta("planilha do fechamento do caixa"), k=2)
    assert resultados[0].texto == "fechamento do caixa gera planilha"
    assert resultados[0].score > resultados[1].score


def test_salvar_de_novo_substitui_os_trechos_antigos():
    store, emb = VectorStore(":memory:"), HashEmbedder()
    _salvar(store, emb, "a.md", ["versão antiga", "outro trecho antigo"], "h1")
    _salvar(store, emb, "a.md", ["versão nova"], "h2")
    assert store.contar_trechos() == 1
    assert store.hash_do_documento("a.md") == "h2"


def test_remover_ausentes_apaga_documentos_e_trechos():
    store, emb = VectorStore(":memory:"), HashEmbedder()
    _salvar(store, emb, "a.md", ["um"])
    _salvar(store, emb, "b.md", ["dois"])
    assert store.remover_ausentes({"a.md"}) == ["b.md"]
    assert [d["documento"] for d in store.listar_documentos()] == ["a.md"]
    assert store.contar_trechos() == 1


def test_busca_em_banco_vazio_nao_quebra():
    assert VectorStore(":memory:").buscar(np.ones(8, dtype=np.float32), k=3) == []
