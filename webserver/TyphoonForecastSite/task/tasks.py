import os
from celery import Celery
from others.settings import BROKER_URL
from util.enum import TaskStateEnum
from task.models import CaseStatus
from others.my_celery import app
from celery import shared_task
from TyphoonForecastSite.celery import app


# ERROR； ValueError: not enough values to unpack (expected 3, got 0)
# TODO:[*] celery 3.1 开始可以通过如下的方式获取task的id

# @shared_task
@app.task(bind=True)
def my_task(self, *args):
    print('测试耗时任务')
    print(f'celery-request-id:{self}')
    print(f'传入的参数为:{args}')
    job = JobInfo(self.request.id)
    job.insert(10)
    print('耗时任务结束')
    print('--------------')


class JobInfo:
    def __init__(self, celery_id: str):
        self.celery_id = celery_id

    def insert(self, rate: int, status: TaskStateEnum = TaskStateEnum.RUNNING):
        insert_model = CaseStatus(celery_id=self.celery_id, case_state=status.value, case_rate=rate)
        insert_model.save()
        pass
