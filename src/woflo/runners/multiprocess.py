from __future__ import annotations

import platform
from typing import TYPE_CHECKING, Any, Callable, Type

from multiprocess.connection import Pipe, _ConnectionBase
from multiprocess.context import ForkProcess, Process, SpawnProcess

from woflo.runners.base import BaseTaskRun
from woflo.util import logger

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
        self.pipe_receive, self.pipe_send = Pipe(duplex=False)

        self.process = self.process_type(target=lambda *args, **kwargs: self.pipe_send.send(fn(*args, **kwargs)), args=args, kwargs=kwargs)

        self.process.start()

    def get_result(self, raise_exceptions: bool = False, wait: bool = True) -> Any:  # noqa: CCR001
        if not wait and self.is_running():
            if raise_exceptions:
                raise RuntimeError(f'Task {self.instance_name} is still running')
            else:
                logger.warn(f'Task {self.instance_name} is still running')
        if self.is_running():
            self.wait()

        self.pipe_send.close()
        try:
            success, res = self.pipe_receive.recv()
        except EOFError:
            logger.warn('Nothing to receive, returning `None`')
            return None
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
