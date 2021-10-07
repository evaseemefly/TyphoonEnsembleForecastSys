import os
from celery import Celery
from conf.settings import CELERY_BROKER_URL, CELERY_TASK_SERIALIZER, CELERY_RESULT_SERIALIZER, \
    CELERY_TASK_RESULT_EXPIRES, CELERY_ACCEPT_CONTENT

# from TyphoonForecastSite import settings

# from task.models import CaseStatus
# 为celery设置环境变量 django -> settings
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TyphoonForecastSite.settings')
# app = Celery(
#     'TyphoonForecastSite',
#     # backend='amqp',
#     broker=BROKER_URL,
#     CELERY_ROUTES={
#         'worker.test1': {'queue': 'test1'}
#     },
# )


app = Celery('CeleryTest')
# settings内关于celery的设置，以CELERY_ 格式书写
app.config_from_object('conf:settings', namespace='CELERY')

app.conf.update(
    CELERY_TASK_SERIALIZER=CELERY_TASK_SERIALIZER,
    CELERY_RESULT_SERIALIZER=CELERY_RESULT_SERIALIZER,
    CELERY_IGNORE_RESULT=True,
    CELERYD_PREFETCH_MULTIPLIER=10,
    CELERYD_MAX_TASKS_PER_CHILD=200,
    CELERY_ACCEPT_CONTENT=CELERY_ACCEPT_CONTENT,
    CELERY_IMPORTS=('task.tasks', 'case.case'),
    BROKER_TRANSPORT_OPTIONS={'visibility_timeout': 3600, 'retry_policy': {
        'timeout': 60 * 60
    }},  # 单位为 s
    CELERY_EVENT_QUEUE_EXPIRES=60 * 60,
    CELERY_EVENT_QUEUE_TTL=60 * 60,
    worker_cancel_long_running_tasks_on_connection_loss=True,
    broker_heartbeat=60 * 60,
    task_acks_on_failure_or_timeout=False,
    # CELERYD_CANCEL_LONG_RUNNING_TASKS_ON_CONNECTION_LOSS=True,
    # BROKER_CONNECTION_RETRY=False,  # 此设置为启动 celery 后 若链接失败是否会重连，需要开启，不能设置为 false

)

# 自动加载所有django app中的tasks任务 ,必须以tasks.py命名
# 自动从所有已注册的django app中加载任务
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# app.autodiscover_tasks()

# bind = True 选项来引用当前任务实例(self)
# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))
#
#
# @app.task(bind=True, name="rename_debug_test")
# def debug_test(self, *args):
#     print('测试耗时任务')
#     print(f'celery-request-id:{self}')
#     print(f'传入的参数为:{args}')
#     # job = JobInfo(self.request.id)
#     # job.insert(10)
#     print('耗时任务结束')
#     print('--------------')
