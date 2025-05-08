from pydantic import BaseModel
from typing import Literal, List, Optional

class Project(BaseModel):
    name: str = "default"
    version: str = "0.0.1"
    description: str = "Default project"
    author: str = ""
    dependencies: list[str] = []

class Serve(BaseModel):
    port: int
    gguf_relative_path: Optional[str] = "model_path/artifacts/model.gguf"
    model_name: str
    alias: Optional[str] = "champion"
    run_id: Optional[str] = None
    model_dir: Optional[str] = "./"
    tracking: Optional[Literal["mlflow"]] = "mlflow"
    serving_tech: Optional[Literal["llamacpp"]] = "llamacpp"

class Litellm(BaseModel):
    model:Optional[str]="openai/custom" 
    api_key:Optional[str]="none"
    api_base:Optional[str]="http://localhost:8080/v1"
    temperature:Optional[float]=0.5
    max_tokens:Optional[int]=1000
    top_p:Optional[float]=1.0
    top_k:Optional[int]=50

class ML(BaseModel):
    type: Optional[Literal["llm", "embeddings"]] = "llm"
    provider: Optional[Literal["local", "litellm"]] = "local"
    serve: Optional[Serve] = None
    litellm: Optional[Litellm] = None

class Observability(BaseModel):
    type: Optional[Literal["phoenix"]] = "phoenix"
    host_type: Optional[Literal["local", "remote"]] = "local"
    api_key: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None

class Config(BaseModel):
    project: Project
    ml: Optional[ML] = None
    serve: Optional[Serve] = None
    litellm: Optional[Litellm] = None
    observability: Optional[Observability] = None


    
    