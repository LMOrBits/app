from serve.experiment_tracker.mlflow.mlflow_llamacpp.manager import ModelManager
from mlflow import MlflowClient
from pyapp.log.log_config import get_logger
from pathlib import Path, PosixPath
from typing import Optional
logger = get_logger()


def get_model_manager(tracking_uri: str, config_path:str|PosixPath, registry_uri: Optional[str]=None ) -> ModelManager:
    """
    Get the model manager for MLflow LlamaCpp.
    
    Args:
        mlflow_client: The MLflow client instance.
    
    Returns:
        ModelManager: The model manager instance.
    """
    # Create and return the model manager
    # tracking_uri = f"http://localhost:{mlflow_port}/"
    registry_uri = registry_uri or tracking_uri
    mlflow_client = MlflowClient(tracking_uri=tracking_uri, registry_uri=registry_uri)
    logger.info(f"Config path: {config_path}")
    logger.info(f"MLflow client: {mlflow_client}")
    experiments = mlflow_client.search_experiments()
    logger.info(f"Experiments: {experiments}")
    # model_config_manager = MLflowModelConfigManager(mlflow_client=mlflow_client, config_path=config_path)
    # model_dir = model_config_manager.add_model("rag_model", alias="champion" , artifact_path="model_path")

    return ModelManager(
      mlflow_client=mlflow_client,
      config_path=Path(config_path).resolve().absolute()
    )