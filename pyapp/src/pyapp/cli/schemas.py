from pydantic import BaseModel
from typing import Literal, List, Optional
class PyappDependency(BaseModel):
    name: str
    directory: str
    local: bool = True
class Project(BaseModel):
    name: str = "default"
    version: str = "0.0.1"
    description: str = "Default project"
    author: str = ""
    dependencies: dict[str, PyappDependency] = {}

class Serve(BaseModel):
    port: int
    # gguf_relative_path: Optional[str] = "model_path/artifacts/model.gguf"
    model_name: str
    alias: Optional[str] = "champion"
    tracking: Optional[Literal["mlflow"]] = "mlflow"
    serving_tech: Optional[Literal["llamacpp"]] = "llamacpp"

class Embeddings(BaseModel):
    port: int
    model_name: str
    alias: Optional[str] = "champion"
    tracking: Optional[Literal["mlflow"]] = "mlflow"
    serving_tech: Optional[Literal["liteserve"]] = "liteserve"

class EmbeddingsLitellm(BaseModel):
    model:str
    dimensions: Optional[int] = None
    encoding_format: Optional[str] = None
    timeout:Optional[int] = 600
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    api_key: Optional[str] = None
    api_type: Optional[str] = None
    caching: bool = False
    user: Optional[str] = None
    custom_llm_provider:Optional[str] = None
    litellm_call_id:Optional[str] = None
    logger_fn:Optional[str] = None

class Litellm(BaseModel):
    model:Optional[str]="openai/custom" 
    api_key:Optional[str]= None
    api_base:Optional[str]= None
    temperature:Optional[float]=0.5
    max_tokens:Optional[int]=1000
    top_p:Optional[float]=1.0
    top_k:Optional[int]=50

class ML(BaseModel):
    type: Optional[Literal["llm", "embeddings"]] = "llm"
    provider: Optional[Literal["local", "litellm"]] = "local"
    model_dir: Optional[str] = None
    serve: Optional[Serve] = None
    embeddings: Optional[Embeddings | EmbeddingsLitellm] = None
    litellm: Optional[Litellm] = None

class Observability(BaseModel):
    type: Optional[Literal["phoenix"]] = "phoenix"
    host_type: Optional[Literal["local", "remote"]] = "local"
    api_key: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None




class VectorDB(BaseModel):
    name: str
    inRepoPath: str
    branchName: str
    sourceBranch: str
    commitHash: Optional[str] = None

class TestData(BaseModel):
    name: str
    inRepoPath: str
    branchName: str
    sourceBranch: str
    commitHash: Optional[str] = None

class Config(BaseModel):
    project: Project
    ml: Optional[ML] = None
    serve: Optional[Serve] = None
    litellm: Optional[Litellm] = None
    observability: Optional[Observability] = None
    vectordb: Optional[VectorDB] = None
    test_data: Optional[TestData] = None