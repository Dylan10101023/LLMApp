import os
import glob
import math
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables so we can get the API key
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL_DEFAULT = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Create a .env file in the project root "
        "with OPENAI_API_KEY=your_key_here"
    )

# Create an OpenAI client with the API key ✅
client = OpenAI(api_key=OPENAI_API_KEY)


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b + 1e-9)


class RAGEngine:
    def __init__(self, data_dir: str, embedding_model: str | None = None):
        self.data_dir = data_dir
        self.embedding_model = embedding_model or EMBEDDING_MODEL_DEFAULT
        self.docs: List[str] = []
        self.embeddings: List[list[float]] = []
        self._load_and_embed_docs()

    def _load_and_embed_docs(self):
        paths = glob.glob(os.path.join(self.data_dir, "*.md")) + \
                glob.glob(os.path.join(self.data_dir, "*.txt"))

        for p in paths:
            with open(p, "r", encoding="utf-8") as f:
                text = f.read()
            chunks = self._chunk_text(text, max_chars=800)
            for chunk in chunks:
                self.docs.append(chunk)
                emb = self._embed(chunk)
                self.embeddings.append(emb)

    def _chunk_text(self, text: str, max_chars: int = 800) -> List[str]:
        words = text.split()
        chunks: List[str] = []
        current: List[str] = []
        current_len = 0

        for w in words:
            if current_len + len(w) + 1 > max_chars:
                chunks.append(" ".join(current))
                current = [w]
                current_len = len(w) + 1
            else:
                current.append(w)
                current_len += len(w) + 1

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _embed(self, text: str) -> list[float]:
        resp = client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return resp.data[0].embedding

    def search(self, query: str, k: int = 4) -> List[str]:
        query_emb = self._embed(query)
        scores = [cosine_similarity(query_emb, e) for e in self.embeddings]
        idx_sorted = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        top_idx = idx_sorted[:k]
        return [self.docs[i] for i in top_idx]