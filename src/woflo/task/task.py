from __future__ import annotations

import logging
import time
from functools import partial
from typing import Any, Callable, Optional, Tuple, Union, cast, overload
from uuid import uuid4

from multiprocess.connection import Pipe, _ConnectionBase
from multiprocess.context import Process

logger = logging.getLogger('woflo')
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)


class Task:
    fn: Callable
    name: Optional[str]
    retries: int
    retry_wait_time: float

    def __init__(self, fn: Callable, name: Optional[str] = None, retries: int = 0, retry_wait_time: float = 0):
        self.fn = fn  # type: ignore
        self.name = name if name else getattr(fn, '__name__', 'task')
        if (retries < 0) or (retries % 1 != 0):
            raise ValueError('`retries` must be a positive integer')
        self.retries = retries
        if retry_wait_time < 0:
            raise ValueError('`retry_wait_time` must be a positive value')
        self.retry_wait_time = retry_wait_time

    def __call__(self, *args: Any, **kwargs: Any) -> TaskRun:  # noqa: CCR001
        instance_name = f'{self.name}-{uuid4()}'
        logger.info(f'Starting task `{instance_name}`')
        send_end, recv_end = Pipe()

        def wrapped_fn(*args: Any, **kwargs: Any) -> None:  # noqa: CCR001
            def retry_block() -> Tuple[bool, Optional[Exception]]:
                try:
                    result = self.fn(*args, **kwargs)
                    send_end.send(result)
                    return (True, None)
                except Exception as e:
                    return (False, e)

            for retry_count in range(self.retries + 1):
                success, exc = retry_block()
                if success:
                    logger.info(f'Finished task {instance_name}')
                    break
                if retry_count < self.retries:
                    logger.info(f'Failed task {instance_name}, retrying in {self.retry_wait_time}s ...')
                    time.sleep(self.retry_wait_time)

            if not success and exc:
                send_end.send(exc)

        p = Process(target=wrapped_fn, args=args, kwargs=kwargs)
        p.start()

        return TaskRun(self, instance_name, p, recv_end)


class TaskRun:
    task: Task
    instance_name: str
    process: Process
    pipe_receive: _ConnectionBase

    def __init__(self, task: Task, instance_name: str, process: Process, pipe_receive: _ConnectionBase):
        self.task = task
        self.instance_name = instance_name
        self.process = process
        self.pipe_receive = pipe_receive

    def get_result(self, wait: bool = True, raise_exceptions: bool = False) -> Any:
        if not wait and self.process.is_alive:
            raise RuntimeError(f'Task {self.instance_name} is still running')
        self.wait()
        result = self.pipe_receive.recv()
        if raise_exceptions and isinstance(result, Exception):
            raise result
        return result

    def wait(self) -> None:
        if self.process.is_alive():
            logger.info(f'Waiting for task {self.instance_name} to finish')
            self.process.join()

    def terminate(self) -> None:
        if self.process.is_alive():
            self.process.terminate()

    def kill(self) -> None:
        if self.process.is_alive():
            self.process.kill()


@overload
def task(fn: Callable) -> Task:
    ...


@overload
def task(
    *,
    name: str = None,
    retries: int = 0,
    retry_wait_time: Union[float, int] = 0,
) -> Callable[[Callable], Task]:
    ...


def task(
    fn: Callable = None,
    *,
    name: str = None,
    retries: int = 0,
    retry_wait_time: Union[float, int] = 0,
) -> Any:
    if fn is None:
        return partial(task, name=name, retries=retries, retry_wait_time=retry_wait_time)
    else:
        if not callable(fn):
            raise ValueError('Wrapped object must be callable')

    return Task(fn=fn, name=name, retries=retries, retry_wait_time=retry_wait_time)
