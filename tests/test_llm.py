import httpx
import pytest

from app.config import Settings
from app.factory import construir_llm
from app.llm import ErroLLM, OllamaLLM


def _ollama(handler):
    return OllamaLLM("qwen2.5:3b", "http://ollama:11434", cliente=httpx.Client(transport=httpx.MockTransport(handler)))


def test_ollama_envia_sistema_e_pergunta_e_le_a_resposta():
    recebido = {}

    def handler(request):
        recebido.update(url=str(request.url), corpo=request.read())
        return httpx.Response(200, json={"message": {"role": "assistant", "content": " Resposta [1]. "}})

    assert _ollama(handler).responder("regras", "pergunta") == "Resposta [1]."
    assert recebido["url"] == "http://ollama:11434/api/chat"
    assert b'"role":"system"' in recebido["corpo"].replace(b" ", b"")
    assert b'"stream":false' in recebido["corpo"].replace(b" ", b"")


def test_ollama_desligado_vira_erro_explicativo():
    def handler(request):
        raise httpx.ConnectError("recusado", request=request)

    with pytest.raises(ErroLLM, match="ollama serve"):
        _ollama(handler).responder("s", "m")


def test_modelo_nao_baixado_explica_como_baixar():
    with pytest.raises(ErroLLM, match="ollama pull qwen2.5:3b"):
        _ollama(lambda r: httpx.Response(404, json={"error": "model not found"})).responder("s", "m")


def test_provedor_padrao_e_o_ollama_gratuito():
    assert isinstance(construir_llm(Settings()), OllamaLLM)


def test_provedor_invalido_e_recusado():
    with pytest.raises(ValueError, match="LLM_PROVIDER"):
        construir_llm(Settings(llm_provider="outro"))
