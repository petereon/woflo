from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from woflo.runners.base import BaseTaskRun

if TYPE_CHECKING:
    from woflo.task import Task


class SequentialTaskRun(BaseTaskRun):
    __result: Any

    def __init__(self, task: Task, instance_name: str, fn: Callable, args: tuple, kwargs: dict):
        super().__init__(task, instance_name, fn, args, kwargs)
        self.task = task
        self.instance_name = instance_name
        self.__result = fn(*args, **kwargs)

    def get_result(self) -> Any:
        super().get_result()
        return self.__result

    def wait(self) -> None:
        super().wait()

    def stop(self) -> None:
        super().stop()

    def is_running(self) -> bool:
        return False
