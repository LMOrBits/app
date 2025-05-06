from pathlib import Path
from typing import Optional
import subprocess
from loguru import logger


def _run_task(category: str, task_name: str, **kwargs: Optional[dict]):
    task_path = Path(__file__).parents[2]
    task_args = [f"'{key.upper()}'={value}" for key, value in kwargs.items() if value is not None]
    command = ["task", "--dir",task_path, f"{category}:{task_name} "] + task_args
    logger.debug(command)
    # Run the Task command
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stderr:
        logger.error(result.stderr)
    if result.stdout:
        logger.info(result.stdout)
    return result

def obsereve_start(observe_port: int = 6666):
    _run_task("local", "observe-start", port=observe_port)

def observe_stop():
    _run_task("local", "observe-stop")

def observe_remove():
    _run_task("local", "observe-remove")

