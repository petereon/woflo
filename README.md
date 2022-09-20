# woflo
## Overview

**woflo** is a Python local-first no-bloat extensible task orchestration framework

Main goal is to abstract a lot of functionality related to Task orchestration and execution away. 

Currently this includes:
- retries
- retry timeout
- parallelism
- logging

## Extensibility

It is designed to be easily extended by developing a custom `Task` runners. Library itself currently exposes two such runners, `MultiprocessTaskRun` and `SequentialTaskRun`.

Additionally `woflo` makes available a `BaseTaskRun`, an interface against which custom runners can be developed.

## Example

Intended usage is by utilizing a decorator `@task`, consider a very simple example which would run 10 sleepy workers in parallel without blocking the main thread:

```python
import time
from woflo import task


@task
def sleepy_worker():
    time.sleep(5)
    print('I am done')


for _ in range(10):
    sleepy_task_run = sleepy_worker()
```

Additionally, you can also include retries for tasks that might fail at times. Following would run attempt to run the enclosed function for 3 times in total with 5 second delay between attempts.

```python
from woflo import task


@task(retries=2, retry_sleep_time=5)
def fetch_data_from_unstable_api():
    ...
```

Furthermore, you can also provide a runner within a `@task` decorator. For example the `SequentialTaskRun` if prefer your tasks to run sequentially and like to wait around a computer a lot. For example:

```python
from woflo import task
from woflo.runners import SequentialTaskRun


@task(runner=SequentialTaskRun)
def sequential_sleepy_worker():
    time.sleep(5)
    print('I am done')


for _ in range(10):
    sleepy_task_run = sequential_sleepy_worker()
```

Each `TaskRun` should also expose a few methods:

- `.get_result()` to fetch the return value of the finished task 
- `.wait()` to block main thread till the task finishes (irrelevant for `SequentialTaskRun` which will block until it finishes anyway)
- `.stop()` to stop the task while its running (irrelevant for `SequentialTaskRun` which will block until it finishes anyway)
- `.is_running()` to check if the task is still running (irrelevant for `SequentialTaskRun` which will block until it finishes anyway)

These can be used simply as:

```python
@task
def read_a_book(book):
    book_pages = iter(book.pages)
    for page in book_pages:
        read(page)
    
    if book.name = 'The Old Man and the Sea'
        return 'A good book'
    else:
        return 'Meh'

def main()
    book = Book('The Old Man and the Sea')

    book_reading = read_a_book(book)

    if book_reading.is_running():
        print('Still reading')
        book_reading_result = book_reading.get_result()
        print(reading_result)

if __name__ == "__main__":
    main()
```






