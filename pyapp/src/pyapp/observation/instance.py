from loguru import logger
from taskpy import TaskCLI
from pathlib import Path
tracer = None

class PhoenixObservation:
  @property
  def port(self):
    return 6006

  @property
  def grpc_port(self):
    return 4317

  def __init__(self):
    self.task = TaskCLI(Path(__file__).parent )
  
  
  def is_running(self):
      try:
        answer = self.task.run("status")
        return int(answer.stdout.strip())!= 0
      except Exception as e:
        logger.error(f"Error in phoenix observation: {e}")
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
      status = self.is_running()
      if not status:
        logger.info("Phoenix is not running")
      else:
        self.task.run("stop")
    except Exception as e:
      logger.error(f"Error in phoenix observation: {e}")
  
  def remove(self):
    try:
      self.task.run("remove")
    except Exception as e:
      logger.error(f"Error in phoenix observation: {e}")


class PhonexLangChainInstrumentor:
  _instance = None
  tracer_provider = None
  
  def __new__(cls, project_name: str = "lmorbits-phoenix", app_name: str = "app1"):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
      cls._instance._initialized = False
    return cls._instance

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

      except Exception as e:
        logger.error(f"Error in phoenix observation: {e}")