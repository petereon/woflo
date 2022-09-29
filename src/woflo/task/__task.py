from __future__ import annotations

import time
from ast import Mult
from functools import partial
from typing import Any, Callable, Optional, Tuple, Type, Union, overload
from uuid import uuid4

from woflo.runners.base import BaseTaskRun
from woflo.runners.multiprocess import MultiprocessTaskRun
from woflo.util import logger


class Task:
    fn: Callable
    name: Optional[str]
    retries: int
    retry_wait_time: float
    runner: Type[BaseTaskRun]

    def __init__(
        self,
        fn: Callable,
        name: Optional[str] = None,
        retries: int = 0,
        retry_wait_time: float = 0,
        runner: Type[BaseTaskRun] = MultiprocessTaskRun,
    ):
        self.fn = fn  # type: ignore
        self.name = name if name else getattr(fn, '__name__', 'task')
        if retries < 0:
            retries = 0
            logger.warn('`retries` must be a positive number, defaulting to 0')
        elif retries % 1 != 0:
            retries = int(round(retries))
            logger.warn(f'`retries` must be a whole number, rounding to {retries}')
        self.retries = retries
        if retry_wait_time < 0:
            retry_wait_time = 0
            logger.warn('`retry_wait_time` must be a positive number, defaulting to 0')
        self.retry_wait_time = retry_wait_time
        self.runner = runner

    def __call__(self, *args: Any, **kwargs: Any) -> BaseTaskRun:  # noqa: CCR001
        instance_name = f'{self.name}-{uuid4()}'

        def wrapped_fn(*args: Any, **kwargs: Any) -> Tuple[bool, Any]:  # noqa: CCR001
            def retry_block() -> Tuple[bool, Any]:
                try:
                    result = self.fn(*args, **kwargs)
                    return True, result
                except Exception as e:
                    return False, e

            for retry_count in range(self.retries + 1):
                success, res = retry_block()
                if success:
                    logger.info(f'Finished task {instance_name}')
                    break
                if retry_count < self.retries:
                    logger.info(f'Failed task {instance_name}, retrying in {self.retry_wait_time}s ...')
                    time.sleep(self.retry_wait_time)

            return success, res

        return self.runner(self, instance_name, wrapped_fn, args, kwargs)


@overload
def task(fn: Callable) -> Task:
    ...  # pragma: no cover


@overload
def task(
    *, name: str = None, retries: int = 0, retry_wait_time: Union[float, int] = 0, runner: Type[BaseTaskRun] = MultiprocessTaskRun
) -> Callable[[Callable], Task]:
    ...  # pragma: no cover


def task(
    fn: Callable = None,
    *,
    name: str = None,
    retries: int = 0,
    retry_wait_time: Union[float, int] = 0,
    runner: Type[BaseTaskRun] = MultiprocessTaskRun,
) -> Any:
    if fn is None:
        return partial(task, name=name, retries=retries, retry_wait_time=retry_wait_time, runner=runner)
    else:
        if not callable(fn):
            raise ValueError('Wrapped object must be callable')

    return Task(fn=fn, name=name, retries=retries, retry_wait_time=retry_wait_time, runner=runner)
