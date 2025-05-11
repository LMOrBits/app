from pathlib import Path
from pyapp.model_connection.lm.langchain.litellm import get_lm_model_manager
from pyapp.cli.schemas import  ML 
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


def get_ml_from_config_dir(config_dir:Path, config_file_name:str):
    config = get_config(config_dir, config_file_name)
    if "ml" not in config:
        raise ValueError("ml not found in config")
    
    ml = ML(**config["ml"])
    return ml

def get_model_embeddings_from_config_dir(config_dir:Path, config_file_name:Optional[str]="appdeps.toml"):
    ml = get_ml_from_config_dir(config_dir, config_file_name)
    return get_model_embeddings(ml)

def get_model_lm_from_config_dir(config_dir:Path, config_file_name:Optional[str]="appdeps.toml"):
    ml = get_ml_from_config_dir(config_dir, config_file_name)
    return get_model_lm(ml)

def get_model_lm( ml:ML):
    assert ml is not None
    if ml.provider == "litellm" and ml.type == "llm":
       from langchain_community.chat_models import ChatLiteLLM 
       args = ml.litellm.model_dump()
       model = ChatLiteLLM(**args)
       return model
    if ml.provider == "local" and ml.type == "llm":
        from pyapp.model_connection.lm.langchain.litellm import get_model_litellm_from_config 
        model = get_model_litellm_from_config(ml)
        return model

def get_model_embeddings( ml:ML):
    if ml.provider == "local" and ml.type == "embeddings":
        from pyapp.model_connection.embeddings.langchain.embeddings import LiteserveEmbeddings
        embedding_model = LiteserveEmbeddings(ml.embeddings)
        return embedding_model
    if ml.provider == "litellm" and ml.type == "embeddings":
        from pyapp.model_connection.embeddings.langchain.embeddings import LitellmEmbeddings
        model = LitellmEmbeddings(ml.embeddings)
        return model
