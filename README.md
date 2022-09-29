# woflo
[![CI](https://github.com/petereon/woflo/actions/workflows/python-test.yml/badge.svg)](https://github.com/petereon/woflo/actions/workflows/python-test.yml)
[![MyPy Lint](https://github.com/petereon/woflo/actions/workflows/python-lint.yml/badge.svg)](https://github.com/petereon/woflo/actions/workflows/python-lint.yml)
[![codecov](https://codecov.io/gh/petereon/woflo/branch/master/graph/badge.svg?token=JDAVYDG3ST)](https://codecov.io/gh/petereon/woflo)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=petereon_woflo&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=petereon_woflo)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=petereon_woflo&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=petereon_woflo)
![PyPI Downloads](https://img.shields.io/pypi/dm/woflo?color=g&label=%F0%9F%93%A5%20Downloads)

## Overview

**woflo** is a Python local-first no-bloat extensible task orchestration framework.

Okay, that's a lot of buzz. So what is actually the point?

Main goal is to abstract a lot of functionality related to Task orchestration and execution away while keeping the "API" clear and dead-simple.

Currently this includes:
- retries
- retry timeout
- parallelism
- logging

## Installation

To download from PyPI use:

```shell
pip install woflo
```

To install from source:

```shell
git clone https://github.com/petereon/woflo.git
cd woflo
poetry build
cd dist
pip install ./woflo-<version>-py3-none-any.whl
```

## Examples

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

You can also include retries for tasks that might fail at times. Following would attempt to run the decorated function for 3 times in total with 5 second delay between attempts.

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

Each `TaskRun` should also expose a few methods that enable you to handle it:

- `.get_result()` to fetch the return value of the finished task 
- `.wait()` to block main thread till the task finishes (irrelevant for `SequentialTaskRun` which will block until it finishes anyway)
- `.stop()` to stop the task while its running (irrelevant for `SequentialTaskRun` which will block until it finishes anyway)
- `.is_running()` to check if the task is still running (irrelevant for `SequentialTaskRun` which will block until it finishes anyway)

Let us define an example task:

```python
import time
from woflo import task

@task
def quick_nap(duration):
    time.sleep(duration)
    if duration < 10
        raise Exception("Ouch oof")
    else:
        return 'Well rested'
```

After you run it,

```python
napping = quick_nap(10)
```

you can check on it to monitor it's state and receive results,

```python
assert napping.is_running()

napping.wait()
assert napping.get_result() == "Well rested"
```

## Task Runners

It is designed to be easily extended by developing a custom `Task` runners. Library itself currently exposes two such runners, `MultiprocessTaskRun` and `SequentialTaskRun`. 

Additionally `woflo` makes available a `BaseTaskRun`, an interface against which custom runners can be developed.

The defualt task runner is `MultiprocessTaskRun`, which can run multiple tasks, or even multiple instances of the same task at the same time in parallel in separate Python process.

### MultiprocessTaskRun

The defualt task runner, which can run multiple tasks, or even multiple instances of the same task at the same time in parallel in separate Python process.

It offers two modes of operation:
- `ForkProcess`, which forks a main process and inherits all of its state. Forking is default on Darwin and Linux (it is not available on Windows)
- `SpawnProcess`, which spawns a new process with same global state

This behavior can be configured by setting the `process_type`:

```python
from woflo.runners.multiprocess import SpawnProcess, MultiprocessTaskRun

MultiprocessTaskRun.process_type = SpawnProcess

@task(runner=MultiprocessTaskRun)
def sleepy_worker():
    time.sleep(5)
    print('I am done')

```

## Roadmap

- [x] ~~Setup GitHub Actions, SonarCloud monitoring and Codecov~~
- [x] ~~Make a PyPI Package~~
- [ ] Decide on final API and create a version 1.x.x
- [ ] Implement a Dask runner
- [ ] Implement a Thread runner
- [ ] Implement an Async runner

## Known issues

- [x] ~~Processes potentially inherint a large in-memory state in MultiprocessTaskRun~~
- [ ] `SpawnProcess` running into `OSError: [Errno 9] Bad file descriptor` on `macOS 12.6` when using `multiprocess.sharedctypes.Value` as reflected in [this issue](https://github.com/uqfoundation/multiprocess/issues/115)
- [ ] Imports need some refactoring
