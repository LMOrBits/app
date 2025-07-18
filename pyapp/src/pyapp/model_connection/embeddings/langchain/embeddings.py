import requests
from typing import List

from langchain_core.embeddings import Embeddings
from litellm import embedding


from pyapp.cli.schemas import Embeddings as EmbeddingsSchema, EmbeddingsLitellm
class LiteserveEmbeddings(Embeddings):
    
    def __init__(self, embeddings: EmbeddingsSchema):
        self.model = embeddings
        self.server = f"http://localhost:{embeddings.port}"

    def __iter__(self):
        return iter([self.model])

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        response = requests.post(f"{self.server}/predict", 
                         json={"input": texts})
        return response.json()["result"]

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self.embed_documents([text])[0]
    
class LitellmEmbeddings(Embeddings):
    
    def __init__(self, embeddings: EmbeddingsLitellm):
        self.args = embeddings.model_dump()

    def __iter__(self):
        return iter([self.args])

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        data = embedding(**self.args, input=texts)["data"]
        return [d["embedding"] for d in data]
    
    def embed_query(self, text: str) -> List[float]:
        return embedding(**self.args, input=[text])["data"][0]["embedding"]