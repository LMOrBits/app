import asyncio
import sys
import time
from contextlib import contextmanager
from functools import wraps
from pathlib import Path

from loguru import logger
from loguru._logger import Logger

logger.level("DEV", no=38, color="<cyan>", icon="⭐")
logger.level("INIT", no=39, color="<green>", icon="🚀🚀🚀🚀")
logger.level("TIME", no=39, color="<yellow>", icon="⌛")
logger.level("LLM", no=15, color="<blue>", icon="🧠")
logger.level("CHECK", no=27, color="<yellow>", icon="✅")


def level_filter(level="DEBUG"):
    def is_level(record):
        return (
            record["level"].no >= logger.level(level).no
            or record["level"].name == "DEV"
        )

    return is_level


def get_logger(**kwargs) -> Logger:
    path = Path(__file__).parent / "logs/error.logs"
    logger.remove()
    log_format = "{time:MMMM D, YYYY > HH:mm:ss} |  {name} : {line} |  <level> {level.icon} {level}  |  {message} </level> "
    if kwargs:
        new_logger = logger.bind(**kwargs)
        new_logger.add(
            path,
            format=log_format + " | {extra}",
            rotation="100 MB",
            retention="10 days",
            level="ERROR",
            backtrace=True,
            diagnose=True,
        )
        new_logger.add(
            sys.stdout, format=log_format + " | {extra} ", filter=level_filter()
        )
        return new_logger
    else:
        logger.add(
            path,
            format=log_format,
            rotation="100 MB",
            retention="10 days",
            level="ERROR",
            backtrace=True,
        )
        logger.add(sys.stdout, format=log_format, filter=level_filter())
        return logger


def log_function_call(logger):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                result = await func(*args, **kwargs)
                end_time = time.time()
                logger.log(
                    "TIME", f"Called {func.__name__}, took {end_time - start_time:.2f}s"
                )
                return result

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                logger.log(
                    "TIME", f"Called {func.__name__}, took {end_time - start_time:.2f}s"
                )
                return result

            return sync_wrapper

    return decorator


@contextmanager
def log_time_context(logger, message: str, level="TIME"):
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.log(level, f"{message} - Completed in {elapsed_time:.2f} seconds")
