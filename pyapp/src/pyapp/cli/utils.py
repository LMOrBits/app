from pathlib import Path
import toml
import click
from pyapp.log.log_config import get_logger
logger = get_logger()

def read_config(give_error:bool=True)->tuple[dict,Path]:
    directory = Path.cwd()
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

def write_config(config:dict,config_dir:str|Path):
    with open(str(config_dir) , "w") as f:
        toml.dump(config, f)