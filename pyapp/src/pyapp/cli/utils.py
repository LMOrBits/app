from pathlib import Path
import toml
import click
from pyapp.log.log_config import get_logger
logger = get_logger()

def read_config(give_error:bool=True, config_path:str=None)->tuple[dict,Path]:
    directory = config_path if config_path else Path.cwd()
    directory = Path(directory)
    config_dir = directory / "appdeps.toml"
    if not config_dir.exists():
        if not give_error:
            return {},config_dir
        else:
            logger.error("appdeps.toml does not exist. Please run 'pyapp init' first.")
            raise ValueError("appdeps.toml does not exist. please run 'pyapp init' first.")
    with open(config_dir, "r") as f:
        config = toml.load(f)
    return config,config_dir

def read_config_from_path(config_path:str)->dict:
    with open(config_path, "r") as f:
        config = toml.load(f)
    return config

def write_config(config:dict,config_dir:str|Path):
    with open(str(config_dir) , "w") as f:
        toml.dump(config, f)