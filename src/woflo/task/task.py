from typing import Any, Callable, Optional

from cytoolz.functoolz import curry

from woflo.util import logger


class Task:
    fn: Callable
    name: Optional[str]

    def __init__(self, fn: Callable, name: Optional[str] = None):
        self.fn = fn  # type: ignore
        self.name = name if name else getattr(fn, '__name__', 'Unnamed')

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        logger.info(f'Starting task `{self.name}`')
        return self.fn(*args, **kwargs)


@curry
def task(fn: Callable, name: Optional[str] = None) -> Task:
    return Task(fn, name)
