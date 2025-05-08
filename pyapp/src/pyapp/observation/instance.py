from loguru import logger
import requests
from taskpy import TaskCLI
from pathlib import Path
tracer = None

class PhoenixObservation:
  _port = 6006
  _grpc_port = 4317
  @property
  def port(self):
    return self._port

  @property
  def grpc_port(self):
    return self._grpc_port

  def __init__(self):
    self.task = TaskCLI(Path(__file__).parent )
  
  
  def is_running(self):
      try:
        answer = self.task.run("status")
        status = int(answer.stdout.strip())!= 0
        if status:
          logger.debug("Phoenix is running")
        else:
          logger.debug("Phoenix is not running")
        return status
      except Exception as e:
        # logger.error(f"Error in phoenix observation: {e}")
        return False 

  def start(self):
    try:
      status = self.is_running()
      if status:
        logger.info("Phoenix is already running")
      else: 
        self.task.run("start", port=self.port, grpc_port=self.grpc_port)
    except Exception as e:
      logger.error(f"Error in phoenix observation: {e}")

  def stop(self):
    try:
      self.task.run("stop")
    except Exception as e:
      logger.error(f"Error in phoenix observation: {e}")
  
  def remove(self):
    try:
      self.task.run("remove")
    except Exception as e:
      logger.error(f"Error in phoenix observation: {e}")


class PhoenixLangChainInstrumentor:
  _instance = None
  tracer_provider = None
  project_url = None
  
  def __new__(cls, project_name: str = "lmorbits-phoenix", app_name: str = "app1"):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
      cls._instance._initialized = False
    return cls._instance

  @staticmethod
  def get_project_url(project_name: str = "lmorbits-phoenix"):
    response = requests.get(
        f"http://localhost:6006/v1/projects/{project_name}",
        headers={"Accept":"*/*"},
    )

    data = response.json()
    project_name= data["data"]["id"]
    return f"http://localhost:{PhoenixObservation._port}/projects/{project_name}"

  def __init__(self, project_name: str = "lmorbits-phoenix", app_name: str = "app1"):
    if not self._initialized:
      try:
        self.app_name = app_name
        self.project_name = project_name
        from opentelemetry import trace
        from openinference.instrumentation.langchain import LangChainInstrumentor
        from phoenix.otel import register

        self.tracer_provider = register(
          project_name=self.project_name,
          set_global_tracer_provider=False,
          verbose=False
        ) 
        LangChainInstrumentor().instrument(tracer_provider=self.tracer_provider)
        trace.set_tracer_provider(self.tracer_provider)
        self._initialized = True
        self.project_url = self.get_project_url(self.project_name)
      except Exception as e:
        logger.error(f"Error in phoenix observation: {e}")