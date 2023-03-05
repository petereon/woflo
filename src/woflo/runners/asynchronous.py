from __future__ import annotations

import asyncio
from time import sleep
from typing import TYPE_CHECKING, Callable, Union

from black import Any

from woflo.runners.base import BaseTaskRun
from woflo.runners.sequential import SequentialTaskRun
from woflo.util import logger

if TYPE_CHECKING:
    from woflo.task import Task  # pragma: no cover


class _AsyncTaskRun(BaseTaskRun):
    asyncio_task: asyncio.Task
    event_loop: asyncio.AbstractEventLoop

    def __init__(self, event_loop: asyncio.AbstractEventLoop, task: Task, instance_name: str, fn: Callable, args: tuple, kwargs: dict):
        super().__init__(task, instance_name, fn, args, kwargs)
        self.task = task
        self.instance_name = instance_name
        self.event_loop = event_loop
        self.asyncio_task = self.event_loop.create_task(self.task.fn(*args, *kwargs))

    async def get_result(self, raise_exceptions: bool = False) -> Any:
        if self.is_running():
            await self.wait()
        try:
            return self.asyncio_task.result()
        except Exception as e:
            if raise_exceptions:
                raise e
            else:
                return e

    async def wait(self) -> None:  # type: ignore
        await asyncio.wait_for(self.asyncio_task, None)

    def stop(self) -> None:
        self.asyncio_task.cancel()

    def is_running(self) -> bool:
        return not self.asyncio_task.done()


def AsyncTaskRun(task: Task, instance_name: str, fn: Callable, args: tuple, kwargs: dict) -> _AsyncTaskRun:
    event_loop = asyncio.get_event_loop()
    return _AsyncTaskRun(event_loop, task, instance_name, fn, args, kwargs)
