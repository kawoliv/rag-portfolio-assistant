"""Linha de comando.

  python -m app.cli indexar               indexa a pasta de documentos (DOCS_DIR)
  python -m app.cli perguntar "pergunta"  responde no terminal, com as fontes
"""

from __future__ import annotations

import argparse
import sys

from .config import Settings
from .factory import construir_rag
from .llm import ErroLLM


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.cli", description="RAG de projetos")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("indexar", help="indexa os documentos da pasta configurada")
    p = sub.add_parser("perguntar", help="faz uma pergunta")
    p.add_argument("pergunta")
    p.add_argument("-k", type=int, default=None, help="quantos trechos recuperar")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    rag = construir_rag(settings)

    if args.comando == "indexar":
        r = rag.indexar_pasta(settings.docs_dir)
        print(f"Indexados: {len(r.indexados)} ({r.trechos} trechos) | "
              f"inalterados: {len(r.inalterados)} | removidos: {len(r.removidos)}")
        return 0

    try:
        resposta = rag.perguntar(args.pergunta, args.k)
    except ErroLLM as erro:
        print(erro, file=sys.stderr)
        return 1
    print(resposta.resposta)
    for f in resposta.fontes:
        print(f"  [{f.n}] {f.documento} > {f.secao} (score {f.score:.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
