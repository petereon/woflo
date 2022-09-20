from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from multiprocess.connection import Pipe, _ConnectionBase
from multiprocess.context import Process

from woflo.runners.base import BaseTaskRun

if TYPE_CHECKING:
    from woflo.task import Task


class MultiprocessTaskRun(BaseTaskRun):
    task: Task
    instance_name: str
    fn: Callable
    process: Process
    pipe_send: _ConnectionBase
    pipe_receive: _ConnectionBase

    def __init__(self, task: Task, instance_name: str, fn: Callable, args: list, kwargs: dict):
        super().__init__(task, instance_name, fn, args, kwargs)
        self.task = task
        self.instance_name = instance_name
        self.pipe_send, self.pipe_receive = Pipe()

        self.process = Process(target=lambda *args, **kwargs: self.pipe_send.send(fn(*args, **kwargs)), args=args, kwargs=kwargs)

        self.process.start()

    def get_result(self, wait: bool = True, raise_exceptions: bool = False) -> Any:
        if not wait and self.is_running():
            raise RuntimeError(f'Task {self.instance_name} is still running')
        if self.is_running():
            self.wait()
        success, res = self.pipe_receive.recv()
        if raise_exceptions and not success:
            raise res
        return res

    def wait(self) -> None:
        super().wait()
        if self.is_running():
            self.process.join()

    def stop(self) -> None:
        super().stop()
        if self.process.is_alive():
            self.process.terminate()

    def is_running(self) -> bool:
        return bool(self.process.is_alive())
