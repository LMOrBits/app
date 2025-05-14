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

def find_config(current_file: str, config_name: str = "appdeps.toml"):
    config_path = Path(current_file).resolve()
    root = Path(config_path.root)
    for parent in [config_path] + list(config_path.parents):
        config_file = parent / config_name
        if config_file.exists():
            return config_file
        if parent == root:
            break
    raise FileNotFoundError(f"Config file not found: {config_name}")

def get_data_dir(current_file: str):
    config_file = find_config(current_file)
    config = get_config(config_file.parent)
    if config.vectordb:
        return config_file.parent / config.vectordb.inRepoPath
    else:
        raise ValueError("No vector store found")



