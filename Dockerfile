FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# PyTorch só para CPU: imagem bem menor que a versão com CUDA
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt requirements-core.txt ./
RUN pip install -r requirements.txt

# Baixa o modelo de embeddings no build, para o container subir sem esperar download
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

COPY app ./app
COPY docs ./docs

EXPOSE 8000
CMD ["sh", "-c", "python -m app.cli indexar && uvicorn app.api:app --host 0.0.0.0 --port 8000"]
