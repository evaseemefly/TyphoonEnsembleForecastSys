import os
# from celery import Celery
from task.celery import app


@app.task(bind=True, name="rename_my_test")
def my_task(self, *args):
    print('测试耗时任务')
    print(f'celery-request-id:{self}')
    print(f'传入的参数为:{args}')
    # job = JobInfo(self.request.id)
    # job.insert(10)
    print('耗时任务结束')
    print('--------------')
