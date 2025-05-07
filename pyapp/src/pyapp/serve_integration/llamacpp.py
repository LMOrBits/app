def delete_all_models_llamacpp():
  from serve.servers.llamacpp.serve import LlamaCppServer
  LlamaCppServer.delete_all()