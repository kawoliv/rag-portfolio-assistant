import pytest

from app.chunking import dividir_markdown


def test_guarda_o_caminho_de_titulos():
    texto = "# Projeto\n\nIntro.\n\n## Instalação\n\nRode pip.\n\n### Docker\n\nUse a imagem.\n"
    trechos = dividir_markdown(texto, "doc.md")
    assert [t.titulo for t in trechos] == [
        "Projeto",
        "Projeto > Instalação",
        "Projeto > Instalação > Docker",
    ]


def test_cerquilha_dentro_de_bloco_de_codigo_nao_vira_titulo():
    texto = "# Uso\n\n```bash\n# comentário do shell\npip install x\n```\n"
    trechos = dividir_markdown(texto, "doc.md")
    assert len(trechos) == 1
    assert "# comentário do shell" in trechos[0].texto


def test_secao_longa_respeita_o_limite_e_cobre_todo_o_texto():
    paragrafos = [f"Parágrafo {i} " + "palavra " * 40 for i in range(12)]
    texto = "# Longo\n\n" + "\n\n".join(paragrafos)
    trechos = dividir_markdown(texto, "doc.md", max_chars=500, overlap=100)
    assert len(trechos) > 1
    assert all(len(t.texto) <= 500 for t in trechos)
    juntos = " ".join(t.texto for t in trechos)
    assert all(f"Parágrafo {i}" in juntos for i in range(12))


def test_secoes_vazias_sao_ignoradas_e_sem_titulo_usa_o_nome_do_arquivo():
    trechos = dividir_markdown("Texto solto.\n\n# Vazio\n\n# Cheio\n\nConteúdo.", "notas.md")
    assert [(t.titulo, t.texto) for t in trechos] == [("notas.md", "Texto solto."), ("Cheio", "Conteúdo.")]


def test_overlap_maior_que_a_janela_e_recusado():
    with pytest.raises(ValueError):
        dividir_markdown("# A\n\ntexto", "a.md", max_chars=100, overlap=100)
