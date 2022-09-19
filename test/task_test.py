from multiprocess import Lock, Value
from ward import raises, skip, test

from woflo.task.task import Task, TaskRun, task


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


@test('Retry wait time cannot be negative')
def _():
    with raises(ValueError) as e:

        @task(retry_wait_time=-2)
        def test_task():
            pass

    assert str(e.raised) == '`retry_wait_time` must be a positive value'


@test('Retries can be set')
def _():
    @task(retries=5)
    def test_task():
        pass

    assert test_task.retries == 5


@test('Retries have to be a positive number')
def _():
    with raises(ValueError) as e:

        @task(retries=-2)
        def test_task():
            pass

    assert str(e.raised) == '`retries` must be a positive integer'


@test('Retries have to be an integer')
def _():
    with raises(ValueError) as e:

        @task(retries=1.2)
        def test_task():
            pass

    assert str(e.raised) == '`retries` must be a positive integer'


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


# @skip('Need to figure out how to properly test multiprocessing process')
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
