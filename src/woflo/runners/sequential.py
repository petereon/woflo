from typing import Any, Callable

from woflo import Task
from woflo.runners.base import BaseTaskRun


class SequentialTaskRun(BaseTaskRun):
    task: Task
    instance_name: str
    fn: Callable
    __result: Any

    def __init__(self, task: Task, instance_name: str, fn: Callable, args: list, kwargs: dict):
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
