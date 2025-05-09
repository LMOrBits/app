import requests
from typing import List

from langchain_core.embeddings import Embeddings
from litellm import embedding


class LiteserveEmbeddings(Embeddings):
    
    def __init__(self, model: str, server: str):
        self.model = model
        self.server = server

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        response = requests.post(f"{self.server}/predict", 
                         json={"input": texts})
        return response.json()["result"]

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self.embed_documents([text])[0]
    
class LitellmEmbeddings(Embeddings):
    
    def __init__(self, model: str):
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return embedding(model=self.model, input=texts)
    
    def embed_query(self, text: str) -> List[float]:
        return embedding(model=self.model, input=[text])[0]