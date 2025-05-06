from loguru import logger
tracer = None

try :
  from openinference.instrumentation.langchain import LangChainInstrumentor
  from phoenix.otel import register
  from opentelemetry import trace
  tracer_provider_mango = register(
      project_name="mango-app",
      set_global_tracer_provider=False,
      verbose=False
  )
  LangChainInstrumentor().instrument(tracer_provider=tracer_provider_mango)
  trace.set_tracer_provider(tracer_provider_mango)
  tracer = trace.get_tracer(__name__)
except Exception as e:
  logger.error(f"Error in phoenix observation: {e}")
