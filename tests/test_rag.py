import pytest

from app.prompts import NAO_ENCONTRADO, SISTEMA


def test_indexa_e_pula_documentos_inalterados(rag, docs):
    primeiro = rag.indexar_pasta(docs)
    assert sorted(primeiro.indexados) == ["caixa.md", "filmes.md"]
    segundo = rag.indexar_pasta(docs)
    assert segundo.indexados == [] and sorted(segundo.inalterados) == ["caixa.md", "filmes.md"]


def test_reindexa_alterados_e_remove_apagados(rag, docs):
    rag.indexar_pasta(docs)
    (docs / "filmes.md").unlink()
    (docs / "caixa.md").write_text("# Caixa\n\nTexto novo.", encoding="utf-8")
    r = rag.indexar_pasta(docs)
    assert r.indexados == ["caixa.md"] and r.removidos == ["filmes.md"]


def test_resposta_usa_o_contexto_certo_e_cita_as_fontes(rag, docs, llm):
    rag.indexar_pasta(docs)
    resposta = rag.perguntar("Como funciona o pagamento em duas formas na venda?")

    assert resposta.encontrou
    sistema, mensagem = llm.chamadas[-1]
    assert sistema == SISTEMA
    assert "<pergunta>Como funciona o pagamento em duas formas na venda?</pergunta>" in mensagem
    assert 'secao="Sistema de caixa &gt; Pagamento dividido"' in mensagem
    # O modelo citou só o [1], então só ele volta como fonte.
    assert [f.n for f in resposta.fontes] == [1]
    assert resposta.fontes[0].documento == "caixa.md"


def test_sem_trecho_relevante_nao_chama_o_modelo(rag, docs, llm):
    rag.indexar_pasta(docs)
    resposta = rag.perguntar("Qual a capital da Mongólia?")
    assert not resposta.encontrou
    assert resposta.resposta == NAO_ENCONTRADO
    assert llm.chamadas == []


def test_pergunta_vazia_e_recusada(rag):
    with pytest.raises(ValueError):
        rag.perguntar("   ")


def test_pasta_inexistente_gera_erro_claro(rag, tmp_path):
    with pytest.raises(FileNotFoundError):
        rag.indexar_pasta(tmp_path / "nao-existe")
