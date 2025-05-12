from pathlib import Path
from pyapp.cli.schemas import  ML 
from typing import Optional
from pyapp.log.log_config import get_logger
from pyapp.utils.config import get_config
logger = get_logger()




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
       logger.debug(f"args: {args}")
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
