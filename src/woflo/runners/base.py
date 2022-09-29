from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from woflo.util import logger

if TYPE_CHECKING:
    from woflo.task import Task  # pragma: no cover


class BaseTaskRun:
    task: Task
    instance_name: str
    fn: Callable

    def __init__(self, task: Task, instance_name: str, fn: Callable, args: tuple, kwargs: dict):
        logger.info(f'Starting task `{instance_name}`')

    def get_result(self, raise_exceptions: bool = False) -> Any:
        pass  # pragma: no cover

    def wait(self) -> None:
        if self.is_running():
            logger.info(f'Waiting for task `{self.instance_name}` to finish')
        else:
            logger.info(f'Task {self.instance_name} is already finished')  # pragma: no cover

    def stop(self) -> None:
        if self.is_running():
            logger.info(f'Killing task `{self.instance_name}`')

    def is_running(self) -> bool:
        pass  # pragma: no cover
