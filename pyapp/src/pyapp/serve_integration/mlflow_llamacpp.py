from mlflow import MlflowClient
from pyapp.log.log_config import get_logger
from pathlib import Path, PosixPath
from typing import Optional 
logger = get_logger()

from serve.servers.llamacpp.serve import LlamaCppServer

from .utils import get_trackning_and_registry_uri 


def get_mlflow_lm_manager( config_path:str|PosixPath, tracking_uri: Optional[str]= None,registry_uri: Optional[str]=None ) -> LlamaCppServer:
    """
    Get the model manager for MLflow LlamaCpp.
    
    Args:
        mlflow_client: The MLflow client instance.
    """

    tracking_uri, registry_uri = get_trackning_and_registry_uri(tracking_uri, registry_uri)
    client = MlflowClient(tracking_uri=tracking_uri, registry_uri=registry_uri)
    manager = LlamaCppServer(config_path, client)
    return manager




