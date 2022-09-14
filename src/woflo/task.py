from typing import Callable, Optional

from cytoolz.functoolz import curry


class Task:
    fn: Callable
    name: Optional[str]

    def __init__(self, fn: Callable, name: Optional[str] = None):
        self.fn = fn  # type: ignore
        self.name = name if name else getattr(fn, "__name__", "Unnamed")


@curry
def task(fn: Callable, name: Optional[str] = None) -> Task:
    return Task(fn, name)
