from langchain_community.chat_models import ChatLiteLLM
import os 
from pydantic import BaseModel
from typing import Optional
from pyapp.log.log_config import get_logger
logger = get_logger()
from pyapp.cli.schemas import ML
class ModelConfig(BaseModel):
  model_name:str
  port:int
  alias:Optional[str]="champion"
  gguf_relative_path:Optional[str]="model_path/artifacts/model.gguf"



def get_model_manager_from_config(config_path:str):
  from pyapp.serve_integration.mlflow_llamacpp import get_model_manager
  tracking_uri = os.getenv("TRACKING_URI")
  registry_uri = os.getenv("REGISTRY_URI")
  assert tracking_uri is not None, "TRACKING_URI is not set"
  logger.info(f"connecing to mlflow ...")
  model_manager = get_model_manager(tracking_uri,config_path, registry_uri)
  return model_manager

def get_model_mlflow_llamacpp(config_path:str,model_config:ModelConfig , **kwargs):
  model_manager = get_model_manager_from_config(config_path)
  model_manager.add_serve(model_config.model_name,port=model_config.port,gguf_relative_path=model_config.gguf_relative_path,alias=model_config.alias)
  args = dict(stream=True,
                    temperature=0.5,
                    verbose=True,
                    model="openai/custom",               
                    api_key="none",                  
                    api_base=f"http://localhost:{model_config.port}/v1")
  args.update(**kwargs)
  return ChatLiteLLM(**args)


def get_model_litellm_from_config(ml:ML):
  if ml.provider == "local" and ml.type == "llm":
    from pyapp.model_connection.lm.langchain.litellm import get_model_mlflow_llamacpp, ModelConfig
    model_config = ModelConfig(
        model_name=ml.serve.model_name,
        alias=ml.serve.alias,
        port=ml.serve.port,
        gguf_relative_path=ml.serve.gguf_relative_path
    )
    litellm_config = ml.litellm.model_dump()
    model = get_model_mlflow_llamacpp(ml.serve.model_dir,model_config,stream=True,**litellm_config)
    return model, 