from pathlib import Path
from typing import Optional, Type, TypeVar
import toml
from pyapp.log.log_config import get_logger
from dotenv import load_dotenv
from omegaconf import OmegaConf
from pydantic import BaseModel
logger = get_logger()

T = TypeVar("T", bound=BaseModel)

def find_config(path: Path, config_file_name: str):
    # check if the appdeps.toml exists if not check parent directory go untill you react the /
    logger.info(f"Searching for config file {config_file_name}")
    while path != path.parent:  # Stop when we reach root directory
        logger.debug(f"Checking {path / config_file_name}")
        config_file = path / config_file_name
        if config_file.exists():
            return config_file
        path = path.parent
    return None  # Return None if no config file is found

def get_config(path: Path, config_file_name: str, env_file_name: Optional[str]= "appdeps.env"):
    config_file = find_config(path, config_file_name)
    if config_file is None:
        raise ValueError(f"Config file {config_file_name} not found in {path}")
    load_dotenv(config_file.parent / env_file_name)
    with open(config_file, "r") as f:
        return toml.load(f)
    
def get_pyapp_config(
    schema_class: Type[T],
    path: Path,
    config_file_name: str = "pyapp.yaml",
    env_file_name: Optional[str] = "appdeps.env"
) -> T:
    config_file = find_config(path, config_file_name)
    if config_file is None:
        raise ValueError(f"Config file {config_file_name} not found in {path}")

    # Load environment variables
    load_dotenv(config_file.parent / env_file_name)

    # Load and parse the YAML config
    omegaconf_config = OmegaConf.load(config_file)
    omegaconf_dict = OmegaConf.to_container(omegaconf_config, resolve=True)
    logger.info(f"omegaconf_dict: {omegaconf_dict}")
    # Return parsed Pydantic model
    return schema_class(**omegaconf_dict)


