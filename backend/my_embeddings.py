# backend/my_embeddings.py
import os
from typing import List

from dotenv import load_dotenv
load_dotenv()


from langchain_core.embeddings import Embeddings
from google import genai
from google.genai import types

# Use env var GEMINI_API_KEY or pass explicitly when creating Client
API_KEY = os.getenv("GEMINI_API_KEY")


class GeminiEmbeddings(Embeddings):
    """
    Minimal embedding wrapper using Google GenAI SDK (Gemini embeddings).
    Returns a list of float vectors for input texts.
    """

    def __init__(self, model: str = "gemini-embedding-001", api_key: str | None = None):
        self.model = model
        self.api_key = api_key or API_KEY
        if not self.api_key:
            raise ValueError("Set GEMINI_API_KEY environment variable with your Gemini API key.")
        # create client
        # genai.Client accepts api_key param; else it looks in env
        self.client = genai.Client(api_key=self.api_key)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # The SDK's embed_content (or models.embed_content) returns embeddings per content
        # We use models.embed_content for batch operation
        # Note: the SDK may return embeddings wrapped in objects; we extract numeric lists.
        response = self.client.models.embed_content(
            model=self.model,
            contents=texts,
            # optionally: config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        # response.embeddings is a list of ContentEmbedding objects
        vectors = []
        for emb in response.embeddings:
            # each emb is usually a types.ContentEmbedding with .values or similar
            # convert to plain Python list of floats
            vals = []
            # handle nested structures robustly
            if hasattr(emb, "values"):
                vals = list(emb.values)
            elif isinstance(emb, dict) and "values" in emb:
                vals = list(emb["values"])
            else:
                # fallback: try to get .embedding or raw list
                if hasattr(emb, "embedding"):
                    vals = list(emb.embedding)
                else:
                    vals = list(emb)
            vectors.append(vals)
        return vectors

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]
