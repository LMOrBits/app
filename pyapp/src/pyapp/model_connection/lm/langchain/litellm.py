from langchain_community.chat_models import ChatLiteLLM

def get_model(api_base:str):
  return ChatLiteLLM(
                    stream=True,
                    temperature=0.5,
                    verbose=True,
                    model="openai/custom",               
                    api_key="none",                  
                    api_base="http://localhost:8080/v1",   
                    )