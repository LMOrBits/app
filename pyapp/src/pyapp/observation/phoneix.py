from .instance import PhoenixLangChainInstrumentor, PhoenixObservation
from openinference.instrumentation import using_session
from openinference.semconv.trace import SpanAttributes
from opentelemetry import trace # wherever your context manager lives
from functools import wraps
from pyapp.log.log_config import get_logger
import base64
from typing import Sequence , Any , TypedDict
logger = get_logger()

import base64
import inspect
from functools import wraps


ph_instrumentor = PhoenixLangChainInstrumentor()
observation = PhoenixObservation()
logger.info("please make sure you have started the observation service via ; `pyapp run`")
# observation.start()

from typing import TypedDict

class AnyMessage(TypedDict):
    content: str

def get_message_content(messages: Any):
    last_message = messages[-1]
    if isinstance(last_message, dict):
        return last_message.get("content","")
    elif isinstance(last_message, str):
        return last_message
    else:
        last_message = last_message.content
        return last_message

def traced_agent(
    name: str,
    propagate_session: bool = True,
    tracer_name: str = "lmorbits-trace"
):
    """
    Decorator that wraps a sync *or* async function in a span named `name`,
    automatically sets SESSION_ID, INPUT_VALUE, and OUTPUT_VALUE,
    and (optionally) enters using_session(session_id) around the call.
    """

    tracer = trace.get_tracer(tracer_name)
    
    

    def decorator(fn):
        is_async = inspect.iscoroutinefunction(fn)

        def _build_span_logic(fn_call):
            """
            Returns a function that, when called, will:
             1) start a span
             2) set session/input attrs
             3) (optionally) run under using_session
             4) capture output attr
             5) return (result, trace_url)
            """
            async def _async_inner(messages, session_id, *args, **kwargs):
                with tracer.start_as_current_span(
                    name=name,
                    attributes={SpanAttributes.OPENINFERENCE_SPAN_KIND: "agent"}
                ) as span:
                    # span/context setup
                    ctx = span.get_span_context()
                    trace_id_hex = format(ctx.trace_id, "032x")
                    st_big = base64.b64encode(f"Span:{ctx.index(0)}".encode("utf-8")).decode("utf-8")
                    trace_url = f"{PhoenixLangChainInstrumentor.get_project_url()}/traces/{trace_id_hex}?selectedSpanNodeId={st_big}"

                    span.set_attribute(SpanAttributes.SESSION_ID, session_id)
                    last_msg = get_message_content(messages)
                    span.set_attribute(SpanAttributes.INPUT_VALUE, last_msg)

                    # invoke under session if desired
                    if propagate_session:
                        async with using_session(session_id):
                            result = await fn_call(messages, session_id, *args, **kwargs)
                    else:
                        result = await fn_call(messages, session_id, *args, **kwargs)

                    output = getattr(result, "content", result)
                    span.set_attribute(SpanAttributes.OUTPUT_VALUE, output)

                    return result, trace_url

            def _sync_inner(messages, session_id, *args, **kwargs):
                with tracer.start_as_current_span(
                    name=name,
                    attributes={SpanAttributes.OPENINFERENCE_SPAN_KIND: "agent"}
                ) as span:
                    # span/context setup
                    ctx = span.get_span_context()
                    trace_id_hex = format(ctx.trace_id, "032x")
                    st_big = base64.b64encode(f"Span:{ctx.index(0)}".encode("utf-8")).decode("utf-8")
                    trace_url = f"{PhoenixLangChainInstrumentor.get_project_url()}/traces/{trace_id_hex}?selectedSpanNodeId={st_big}"

                    span.set_attribute(SpanAttributes.SESSION_ID, session_id)
                    last_msg = get_message_content(messages)
                    span.set_attribute(SpanAttributes.INPUT_VALUE, last_msg)

                    # invoke under session if desired
                    if propagate_session:
                        with using_session(session_id):
                            result = fn_call(messages, session_id, *args, **kwargs)
                    else:
                        result = fn_call(messages, session_id, *args, **kwargs)

                    output = getattr(result, "content", result)
                    span.set_attribute(SpanAttributes.OUTPUT_VALUE, output)

                    return result, trace_url

            return _async_inner if is_async else _sync_inner

        wrapped = _build_span_logic(fn)
        wrapped = wraps(fn)(wrapped)
        return wrapped

    return decorator

def async_generator_traced_agent(
    name: str,
    propagate_session: bool = True,
    tracer_name: str = "lmorbits-trace"
):
    """
    Decorator for async generator functions that wraps them in a span named `name`,
    automatically sets SESSION_ID, INPUT_VALUE, and OUTPUT_VALUE,
    and (optionally) enters using_session(session_id) around the call.
    Supports functions that use async for and yield results.
    """
    tracer = trace.get_tracer(tracer_name)

    def decorator(fn):
        if not inspect.isasyncgenfunction(fn):
            raise TypeError("async_generator_traced_agent can only be used with async generator functions")

        @wraps(fn)
        async def wrapped(messages, session_id, *args, **kwargs):
            with tracer.start_as_current_span(
                name=name,
                attributes={SpanAttributes.OPENINFERENCE_SPAN_KIND: "agent"}
            ) as span:
                # span/context setup
                ctx = span.get_span_context()
                trace_id_hex = format(ctx.trace_id, "032x")
                st_big = base64.b64encode(f"Span:{ctx.index(0)}".encode("utf-8")).decode("utf-8")
                trace_url = f"{PhoenixLangChainInstrumentor.get_project_url()}/traces/{trace_id_hex}?selectedSpanNodeId={st_big}"

                span.set_attribute(SpanAttributes.SESSION_ID, session_id)
                last_msg = get_message_content(messages)
                span.set_attribute(SpanAttributes.INPUT_VALUE, last_msg)

                # invoke under session if desired
                if propagate_session:
                    async with using_session(session_id):
                        async for result in fn(messages, session_id, *args, **kwargs):
                            output = getattr(result, "content", result)
                            span.set_attribute(SpanAttributes.OUTPUT_VALUE, output)
                            yield result, trace_url
                else:
                    async for result in fn(messages, session_id, *args, **kwargs):
                        output = getattr(result, "content", result)
                        span.set_attribute(SpanAttributes.OUTPUT_VALUE, output)
                        yield result, trace_url

        return wrapped

    return decorator

# @traced_agent(name="app1")
# def assistant2(messages: list[dict], session_id: str):
#     # now you only have to do your business logic
#     return chain.invoke(messages)