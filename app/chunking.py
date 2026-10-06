"""Divide documentos Markdown em trechos (chunks) para indexação.

Estratégia:
1. Separa o texto por seções, guardando o caminho de títulos (ex.: "Sistema > Como rodar").
   Linhas com "#" dentro de blocos de código não contam como título.
2. Seções curtas viram um trecho só. Seções longas são quebradas em janelas de até
   `max_chars`, cortando de preferência entre parágrafos e com sobreposição de
   `overlap` caracteres, para não perder contexto na fronteira entre trechos.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")


@dataclass(frozen=True)
class Chunk:
    titulo: str
    texto: str


def _secoes(texto: str) -> list[tuple[str, str]]:
    """Retorna pares (caminho de títulos, conteúdo) na ordem do documento."""
    secoes: list[tuple[str, list[str]]] = []
    pilha: list[tuple[int, str]] = []
    atual: list[str] = []
    dentro_de_codigo = False

    def fechar() -> None:
        caminho = " > ".join(t for _, t in pilha)
        secoes.append((caminho, atual.copy()))

    for linha in texto.splitlines():
        if _FENCE.match(linha):
            dentro_de_codigo = not dentro_de_codigo
            atual.append(linha)
            continue
        m = None if dentro_de_codigo else _HEADING.match(linha)
        if m:
            fechar()
            atual.clear()
            nivel, titulo = len(m.group(1)), m.group(2).strip()
            while pilha and pilha[-1][0] >= nivel:
                pilha.pop()
            pilha.append((nivel, titulo))
        else:
            atual.append(linha)
    fechar()

    return [(caminho, "\n".join(linhas).strip()) for caminho, linhas in secoes]


def _janelas(texto: str, max_chars: int, overlap: int) -> list[str]:
    """Quebra um texto longo em janelas, preferindo cortar entre parágrafos."""
    if len(texto) <= max_chars:
        return [texto]

    paragrafos = [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]
    pedacos: list[str] = []
    for p in paragrafos:  # parágrafos maiores que a janela são cortados à força
        while len(p) > max_chars:
            pedacos.append(p[:max_chars])
            p = p[max_chars - overlap :]
        pedacos.append(p)

    janelas: list[str] = []
    atual = ""
    for p in pedacos:
        candidato = f"{atual}\n\n{p}" if atual else p
        if len(candidato) <= max_chars:
            atual = candidato
            continue
        janelas.append(atual)
        cauda = atual[-overlap:] if overlap else ""
        atual = f"{cauda}\n\n{p}" if cauda and len(cauda) + len(p) + 2 <= max_chars else p
    if atual:
        janelas.append(atual)
    return janelas


def dividir_markdown(
    texto: str, nome_documento: str, max_chars: int = 1200, overlap: int = 200
) -> list[Chunk]:
    if overlap >= max_chars:
        raise ValueError("overlap precisa ser menor que max_chars")

    trechos: list[Chunk] = []
    for caminho, conteudo in _secoes(texto):
        if not conteudo:
            continue
        titulo = caminho or nome_documento
        for janela in _janelas(conteudo, max_chars, overlap):
            trechos.append(Chunk(titulo=titulo, texto=janela))
    return trechos
