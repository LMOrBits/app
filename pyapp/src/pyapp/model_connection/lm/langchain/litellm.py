from langchain_community.chat_models import ChatLiteLLM
from typing import Optional
from pyapp.log.log_config import get_logger
logger = get_logger()
from pyapp.cli.schemas import ML, Serve
from pyapp.serve_integration.mlflow_llamacpp import get_mlflow_lm_manager
from pydantic import BaseModel

class ModelConfig(BaseModel):
  model_name:str
  alias:Optional[str]="champion"
  port:int


def get_lm_model_manager(config_path:str):
  model_manager = get_mlflow_lm_manager(config_path)
  return model_manager


def get_litellm_model_from_config_mlflow(**kwargs):

  args = dict(stream=True,
                    temperature=0.5,
                    verbose=True,
                    model="openai/custom",               
                    api_key="none",                  
                    api_base=f"http://localhost:{model_config.port}/v1")
  args.update(**kwargs)
  return ChatLiteLLM(**args)


def get_model_litellm_from_config(ml:ML):
  litellm_config = ml.litellm.model_dump()
  litellm_config.update(stream=True)
  model = ChatLiteLLM(**litellm_config)
  return model

  