import os
from celery import Celery
from others.settings import BROKER_URL, CELERY_RESULT_BACKEND, CELERY_TASK_SERIALIZER, CELERY_RESULT_SERIALIZER, \
    CELERY_TASK_RESULT_EXPIRES, CELERY_ACCEPT_CONTENT
from TyphoonForecastSite import settings

# from task.models import CaseStatus
# 为celery设置环境变量 django -> settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TyphoonForecastSite.settings')
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
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    CELERY_TASK_SERIALIZER=CELERY_TASK_SERIALIZER,
    CELERY_RESULT_SERIALIZER=CELERY_RESULT_SERIALIZER,
    CELERY_IGNORE_RESULT=True,
    CELERYD_PREFETCH_MULTIPLIER=10,
    CELERYD_MAX_TASKS_PER_CHILD=200,
    CELERY_ACCEPT_CONTENT=CELERY_ACCEPT_CONTENT
)

# 自动加载所有django app中的tasks任务 ,必须以tasks.py命名
# 自动从所有已注册的django app中加载任务
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# app.autodiscover_tasks()

# bind = True 选项来引用当前任务实例(self)
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
