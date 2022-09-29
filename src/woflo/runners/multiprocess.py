from __future__ import annotations

import platform
from typing import TYPE_CHECKING, Any, Callable, Type

from multiprocess.connection import Pipe, _ConnectionBase
from multiprocess.context import ForkProcess, Process, SpawnProcess

from woflo.runners.base import BaseTaskRun

if TYPE_CHECKING:
    from woflo.task import Task  # pragma: no cover


class MultiprocessTaskRun(BaseTaskRun):
    process: Process
    pipe_send: _ConnectionBase
    pipe_receive: _ConnectionBase
    process_type: Type[Process] = ForkProcess if not platform.system() == 'Windows' else SpawnProcess

    def __init__(self, task: Task, instance_name: str, fn: Callable, args: tuple, kwargs: dict):
        super().__init__(task, instance_name, fn, args, kwargs)
        self.task = task
        self.instance_name = instance_name
        self.pipe_send, self.pipe_receive = Pipe()

        self.process = self.process_type(target=lambda *args, **kwargs: self.pipe_send.send(fn(*args, **kwargs)), args=args, kwargs=kwargs)

        self.process.start()

    def get_result(self, raise_exceptions: bool = False, wait: bool = True) -> Any:
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
