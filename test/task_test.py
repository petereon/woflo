import asyncio
import time
from unittest.mock import patch

from multiprocess import Lock, Value
from ward import raises, skip, test

from woflo.runners import AsyncTaskRun, MultiprocessTaskRun, SequentialTaskRun
from woflo.task import Task, task


@test('Callable decorated with `task` becomes a Task')
def _():
    @task
    def test_task():
        return 1

    assert isinstance(test_task, Task)
    assert test_task.fn() == 1


@test('Task can be named')
def _():
    @task(name='Try Task')
    def test_task():
        pass

    assert test_task.name == 'Try Task'


@test('Retry wait time can be set')
def _():
    @task(retry_wait_time=5)
    def test_task():
        pass

    assert test_task.retry_wait_time == 5


@test('Set `retry_wait_time` to 0 when negative')
def _():
    @task(retry_wait_time=-2)
    def test_task():
        pass

    assert test_task.retry_wait_time == 0


@test('Retries can be set')
def _():
    @task(retries=5)
    def test_task():
        pass

    assert test_task.retries == 5


@test('Set `retries` to 0 when negative')
def _():
    @task(retries=-2)
    def test_task():
        pass

    assert test_task.retries == 0


@test('Round retries if not integer')
def _():
    @task(retries=3.2)
    def test_task():
        pass

    assert test_task.retries == 3


@test('Wrapped object has to be callable')
def _():
    with raises(ValueError) as e:
        task('something')

    assert str(e.raised) == 'Wrapped object must be callable'


@test('Initializing task with the class')
def _():
    def test_function():
        return 1

    test_task = Task(test_function, 'Test function')

    assert test_task.fn() == 1
    assert test_task.name == 'Test function'


@test('Running task and getting a result')
def _():
    @task
    def add_two(num):
        return num + 2

    task_run = add_two(3)

    res = task_run.get_result()

    assert res == 5


@test('Running a failing task with retries')
def _():
    val = Value('i', 0)
    lock = Lock()

    @task(retries=3)
    def failing(val, lock):
        with lock:
            val.value += 1
        raise Exception('Test fail')

    failing(val, lock).wait()

    assert val.value == 4


@test('Running a failing task and raising an exception')
def _():
    @task
    def failing():
        raise Exception('Test fail')

    with raises(Exception) as e:
        failing().get_result(raise_exceptions=True)

    assert str(e.raised) == 'Test fail'


@test('Stopping a task')
def _():
    @task
    def stopped():
        time.sleep(10)

    stopped_task_run = stopped()

    assert stopped_task_run.process.is_alive()
    stopped_task_run.stop()
    time.sleep(1)
    assert not stopped_task_run.process.is_alive()


@test('Getting value without waiting')
def _():
    @task
    def test_task():
        time.sleep(2)

    test_task_run = test_task()
    with raises(RuntimeError) as e:
        test_task_run.get_result(wait=False, raise_exceptions=True)
    assert str(e.raised) == f'Task {test_task_run.instance_name} is still running'


@test('Task runner can be set to `SequentialTaskRun`')
def _():
    @task(runner=SequentialTaskRun)
    def test_task():
        return 1

    assert isinstance(test_task, Task)
    assert test_task.fn() == 1


@test('`SequentialTaskRun` returns properly')
def _():
    @task(runner=SequentialTaskRun)
    def test_task():
        return 1

    assert test_task().get_result() == 1


@test('`SequentialTaskRun` returns exception when `raise_exceptions` is not set')
def _():
    @task(runner=SequentialTaskRun)
    def test_task():
        raise Exception('Failing Task')

    res = test_task().get_result()
    assert str(res) == 'Failing Task'
    assert isinstance(res, Exception)


@test('`SequentialTaskRun` returns exception when `raise_exceptions` is set to `False`')
def _():
    @task(runner=SequentialTaskRun)
    def test_task():
        raise Exception('Failing Task')

    res = test_task().get_result(raise_exceptions=False)
    assert str(res) == 'Failing Task'
    assert isinstance(res, Exception)


@test('`SequentialTaskRun` returns exception when `raise_exceptions` is set to `True`')
def _():
    @task(runner=SequentialTaskRun)
    def test_task():
        raise Exception('Failing Task')

    with raises(Exception) as e:
        test_task().get_result(raise_exceptions=True)
    assert str(e.raised) == 'Failing Task'


@test('`MultiprocessTaskRun` returns exception when `raise_exceptions` is not set')
def _():
    @task(runner=MultiprocessTaskRun)
    def test_task():
        raise Exception('Failing Task')

    res = test_task().get_result()
    assert str(res) == 'Failing Task'
    assert isinstance(res, Exception)


@test('`MultiprocessTaskRun` returns exception when `raise_exceptions` is set to `False`')
def _():
    @task(runner=MultiprocessTaskRun)
    def test_task():
        raise Exception('Failing Task')

    res = test_task().get_result(raise_exceptions=False)
    assert str(res) == 'Failing Task'
    assert isinstance(res, Exception)


@test('`MultiprocessTaskRun` returns exception when `raise_exceptions` is set to `True`')
def _():
    @task(runner=MultiprocessTaskRun)
    def test_task():
        raise Exception('Failing Task')

    with raises(Exception) as e:
        test_task().get_result(raise_exceptions=True)
    assert str(e.raised) == 'Failing Task'


@test('`AsyncTaskRun` runs asynchronously')
async def _():
    @task(runner=AsyncTaskRun)
    async def task1():
        await asyncio.sleep(1)
        return 1

    @task(runner=AsyncTaskRun)
    async def task2():
        await asyncio.sleep(2)
        return 2

    start = time.time()

    task_run1 = task1()
    task_run2 = task2()

    res1 = await task_run1.get_result()
    res2 = await task_run2.get_result()

    assert res1 == 1
    assert res2 == 2
    assert (time.time() - start) < 3


@test('`AsyncTaskRun`s can block themselves')
async def _():
    @task(runner=AsyncTaskRun)
    async def task1():
        await asyncio.sleep(2)
        return 1

    @task(runner=AsyncTaskRun)
    async def task2():
        await asyncio.sleep(2)
        return 2

    start = time.time()

    task_run1 = task1()
    await task_run1.wait()
    task_run2 = task2()
    await task_run2.wait()

    assert (time.time() - start) > 4
