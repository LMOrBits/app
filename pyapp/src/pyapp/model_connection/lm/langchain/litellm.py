from langchain_community.chat_models import ChatLiteLLM
import os 
from pydantic import BaseModel
from typing import Optional
from pyapp.log.log_config import get_logger
logger = get_logger()

class ModelConfig(BaseModel):
  model_name:str
  port:int
  gguf_relative_path:Optional[str]="model_path/artifacts/model.gguf"


def get_model_mlflow_llamacpp(tracking_uri:str,config_path:str,model_config:ModelConfig, registry_uri:Optional[str]=None , **kwargs):
  from pyapp.serve_integration.mlflow_llamacpp import get_model_manager
  model_manager = get_model_manager(tracking_uri,config_path, registry_uri)
  logger.info(f"connecing to mlflow ...")
  model_manager.add_serve(model_config.model_name,port=model_config.port,gguf_relative_path=model_config.gguf_relative_path)
  args = dict(stream=True,
                    temperature=0.5,
                    verbose=True,
                    model="openai/custom",               
                    api_key="none",                  
                    api_base=f"http://localhost:{model_config.port}/v1")
  args.update(**kwargs)
  return ChatLiteLLM(**args)

