import time
from random import randint

from woflo import task


@task(retries=2, retry_wait_time=2)
def sleepy_sum(a: int, b: int) -> int:
    time.sleep(a + b)
    if randint(1, 5) > 2:
        raise Exception('Failed')
    return a + b


def workflow(sleepers: int = 5) -> None:
    task_runs = []
    for i in range(sleepers):
        task_runs.append(sleepy_sum(i, 2))

    results = [task_run.get_result() for task_run in task_runs]

    print(results)


if __name__ == '__main__':
    workflow()
