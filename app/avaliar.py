"""Avaliação da recuperação: a busca encontra o documento certo para cada pergunta?

Lê eval/perguntas.json e mede o acerto@k (a pergunta conta como acerto se o documento
esperado aparece entre os k trechos mais parecidos). Não chama o modelo de linguagem,
então roda de graça e serve para comparar ajustes de chunking, modelo de embedding e k.

  python -m app.avaliar            usa TOP_K da configuração
  python -m app.avaliar -k 2
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import Settings
from .embeddings import SentenceTransformerEmbedder
from .rag import RAG
from .store import VectorStore


def avaliar(rag: RAG, casos: list[dict], k: int) -> dict:
    acertos, detalhes = 0, []
    for caso in casos:
        resultados = rag.recuperar(caso["pergunta"], k)
        documentos = [r.documento for r in resultados]
        acertou = caso["documento_esperado"] in documentos
        acertos += acertou
        detalhes.append({"pergunta": caso["pergunta"], "acertou": acertou, "top": documentos})
    return {"k": k, "acerto": acertos / len(casos) if casos else 0.0, "detalhes": detalhes}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.avaliar")
    parser.add_argument("-k", type=int, default=None)
    parser.add_argument("--casos", default="eval/perguntas.json")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    rag = RAG(VectorStore(settings.db_path), SentenceTransformerEmbedder(settings.embedding_model),
              llm=None, top_k=settings.top_k)  # type: ignore[arg-type]
    rag.indexar_pasta(settings.docs_dir)
    casos = json.loads(Path(args.casos).read_text(encoding="utf-8"))
    resultado = avaliar(rag, casos, args.k or settings.top_k)

    for d in resultado["detalhes"]:
        print(f"{'OK ' if d['acertou'] else 'ERRO'}  {d['pergunta']}  ->  {', '.join(d['top'])}")
    print(f"\nAcerto@{resultado['k']}: {resultado['acerto']:.0%} ({len(casos)} perguntas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
