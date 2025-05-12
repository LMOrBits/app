from pathlib import Path
from typing import Optional
import toml
from pyapp.log.log_config import get_logger
from dotenv import load_dotenv
logger = get_logger()

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