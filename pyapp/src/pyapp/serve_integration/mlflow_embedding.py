from mlflow import MlflowClient
from pyapp.log.log_config import get_logger
from pathlib import Path, PosixPath
from typing import Optional 
from .utils import get_trackning_and_registry_uri
logger = get_logger()

from serve.servers.embedding.main import EmbeddingManager


def get_mlflow_embeddings_manager( config_path:str|PosixPath, tracking_uri: Optional[str]= None,registry_uri: Optional[str]=None ) -> EmbeddingManager:
    """
    Get the model manager for MLflow LlamaCpp.
    
    Args:
        mlflow_client: The MLflow client instance.
    """

    tracking_uri, registry_uri = get_trackning_and_registry_uri(tracking_uri, registry_uri)
    client = MlflowClient(tracking_uri=tracking_uri, registry_uri=registry_uri)
    manager = EmbeddingManager(config_path, client)
    return manager