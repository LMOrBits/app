import os
from typing import Optional, Tuple

def get_trackning_and_registry_uri(tracking_uri: Optional[str]= None,registry_uri: Optional[str]=None ) -> Tuple[str, str]:
    """
    Get the tracking and registry URI.
    """
    if tracking_uri is None:
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
        assert tracking_uri is not None, "MLFLOW_TRACKING_URI is not set"
    if registry_uri is None:
        registry_uri = os.getenv("MLFLOW_REGISTRY_URI")
        if registry_uri is None:
            registry_uri = tracking_uri
    return tracking_uri, registry_uri