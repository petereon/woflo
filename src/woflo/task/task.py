from multiprocessing import Pipe, Process
from multiprocessing.connection import _ConnectionBase
from typing import Any, Callable, Optional
from uuid import uuid4

from cytoolz.functoolz import curry

from woflo.util import logger


class Task:
    fn: Callable
    name: Optional[str]

    def __init__(self, fn: Callable, name: Optional[str] = None):
        self.fn = fn  # type: ignore
        self.name = name if name else getattr(fn, '__name__', 'Unnamed')

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        instance_name = f'{uuid4()}-{self.name}'
        logger.info(f'Starting task `{instance_name}`')
        send_end, recv_end = Pipe(False)

        def wrapped_fn(*args: Any, **kwargs: Any) -> None:
            send_end.send(self.fn(args=args, kwargs=kwargs))
            logger.info(f'Finished task {instance_name}')

        p = Process(target=wrapped_fn, args=args, kwargs=kwargs)

        return RunningTaskInstance(self, instance_name, p, recv_end)


class RunningTaskInstance:
    task: Task
    instance_name: str
    process: Process
    pipe_receive: _ConnectionBase

    def __init__(self, task: Task, instance_name: str, process: Process, pipe_receive: _ConnectionBase):
        self.task = task
        self.instance_name = instance_name
        self.process = process
        self.pipe_receive = pipe_receive

    def get_result(self) -> Any:
        if self.process.is_alive():
            logger.info(f'Waiting for task {self.instance_name} to finish')
            self.process.join()
        return self.pipe_receive.recv()


@curry
def task(fn: Callable, name: Optional[str] = None) -> Task:
    return Task(fn, name)
