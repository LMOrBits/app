from .instance import PhoenixLangChainInstrumentor, PhoenixObservation
from openinference.instrumentation import using_session
from openinference.semconv.trace import SpanAttributes
from opentelemetry import trace # wherever your context manager lives
from functools import wraps
from pyapp.log.log_config import get_logger
import base64
logger = get_logger()

ph_instrumentor = PhoenixLangChainInstrumentor()
observation = PhoenixObservation()
logger.info("Starting Phoenix observation")
observation.start()

def traced_agent(name: str, propagate_session: bool = True, tracer_name:str="lmorbits-trace"):
    """
    Decorator that wraps a function in a span named `name`,
    automatically sets SESSION_ID, INPUT_VALUE, and OUTPUT_VALUE,
    and (optionally) enters using_session(session_id) around the call.
    """
    tracer = trace.get_tracer(tracer_name)
    def decorator(fn):
        @wraps(fn)
        def wrapper(messages: list[dict], session_id: str, *args, **kwargs):
            # start the OpenTelemetry span
            with tracer.start_as_current_span(
                name=name,
                attributes={SpanAttributes.OPENINFERENCE_SPAN_KIND: "agent"}
            ) as span:
                # record session and input
                trace_id = span.get_span_context().trace_id
                span_id = span.get_span_context().index(0)
                text = f"Span:{span_id}"
                st_big = base64.b64encode(text.encode("utf-8")).decode("utf-8")
                trace_id_hex = format(trace_id, "032x")  # Converts to 32-character hex
                
                trace_url = f"{ph_instrumentor.project_url}/traces/{trace_id_hex}?selectedSpanNodeId={st_big}"
                
                span.set_attribute(SpanAttributes.SESSION_ID, session_id)
                last_msg = messages[-1].get("content")
                span.set_attribute(SpanAttributes.INPUT_VALUE, last_msg)

                # optionally propagate session into sub‐spans
                if propagate_session:
                    with using_session(session_id):
                        result = fn(messages, session_id, *args, **kwargs)
                else:
                    result = fn(messages, session_id, *args, **kwargs)

                # record the output
                # assume returned object has .content
                output = getattr(result, "content", result)
                span.set_attribute(SpanAttributes.OUTPUT_VALUE, output)

                return result,trace_url
        return wrapper
    return decorator


# @traced_agent(name="app1")
# def assistant2(messages: list[dict], session_id: str):
#     # now you only have to do your business logic
#     return chain.invoke(messages)