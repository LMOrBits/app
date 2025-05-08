from pathlib import Path
from pyapp.cli.schemas import Config
import toml

def get_config(config_path:str):
    config_path = Path(config_path)/ "appdeps.toml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r") as f:
        config = toml.load(f)
    return Config(**config)


