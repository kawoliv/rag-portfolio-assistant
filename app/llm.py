"""Camada de geração de texto.

`OllamaLLM` roda um modelo aberto localmente pelo Ollama: gratuito, sem chave e offline.
`ClaudeLLM` chama a API da Anthropic (paga; lê a chave de ANTHROPIC_API_KEY).
`FakeLLM` devolve respostas prontas e guarda o último prompt, para os testes.
"""

from __future__ import annotations

from typing import Protocol

import httpx


class ErroLLM(RuntimeError):
    """Falha ao gerar a resposta (rede, chave inválida, limite de uso etc.)."""


class LLM(Protocol):
    def responder(self, sistema: str, mensagem: str) -> str: ...


class OllamaLLM:
    def __init__(
        self,
        modelo: str,
        url: str = "http://localhost:11434",
        max_tokens: int = 800,
        timeout: float = 180.0,
        cliente: httpx.Client | None = None,
    ) -> None:
        self.modelo = modelo
        self.url = url.rstrip("/")
        self.max_tokens = max_tokens
        self._cliente = cliente or httpx.Client(timeout=timeout)

    def responder(self, sistema: str, mensagem: str) -> str:
        corpo = {
            "model": self.modelo,
            "messages": [
                {"role": "system", "content": sistema},
                {"role": "user", "content": mensagem},
            ],
            "stream": False,
            # Temperatura baixa: em RAG queremos fidelidade ao contexto, não criatividade.
            "options": {"temperature": 0.2, "num_predict": self.max_tokens},
        }
        try:
            r = self._cliente.post(f"{self.url}/api/chat", json=corpo)
        except httpx.ConnectError as erro:
            raise ErroLLM(
                f"Não consegui falar com o Ollama em {self.url}. Ele está aberto? "
                "Instale em ollama.com e rode `ollama serve`."
            ) from erro
        except httpx.TimeoutException as erro:
            raise ErroLLM("O modelo demorou demais para responder. Tente um modelo menor.") from erro

        if r.status_code == 404:
            raise ErroLLM(f"Modelo '{self.modelo}' não encontrado. Baixe com: ollama pull {self.modelo}")
        if r.status_code >= 400:
            raise ErroLLM(f"O Ollama respondeu com erro {r.status_code}: {r.text[:200]}")
        return r.json().get("message", {}).get("content", "").strip()


class ClaudeLLM:
    def __init__(self, modelo: str, max_tokens: int = 800) -> None:
        import anthropic

        self._anthropic = anthropic
        self._cliente = anthropic.Anthropic()
        self.modelo = modelo
        self.max_tokens = max_tokens

    def responder(self, sistema: str, mensagem: str) -> str:
        try:
            resposta = self._cliente.messages.create(
                model=self.modelo,
                max_tokens=self.max_tokens,
                system=sistema,
                messages=[{"role": "user", "content": mensagem}],
            )
        except self._anthropic.APIError as erro:
            raise ErroLLM(f"Falha ao consultar o modelo: {erro}") from erro
        return "".join(b.text for b in resposta.content if b.type == "text").strip()


class FakeLLM:
    def __init__(self, resposta: str = "Resposta de teste [1].") -> None:
        self.resposta = resposta
        self.chamadas: list[tuple[str, str]] = []

    def responder(self, sistema: str, mensagem: str) -> str:
        self.chamadas.append((sistema, mensagem))
        return self.resposta
