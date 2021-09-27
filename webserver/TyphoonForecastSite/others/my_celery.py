import os
from celery import Celery
from others.settings import BROKER_URL, CELERY_RESULT_BACKEND, CELERY_TASK_SERIALIZER, CELERY_RESULT_SERIALIZER, \
    CELERY_TASK_RESULT_EXPIRES, CELERY_ACCEPT_CONTENT
from TyphoonForecastSite import settings

# from task.models import CaseStatus
# 为celery设置环境变量 django -> settings
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TyphoonForecastSite.settings')
app = Celery(
    # 'TyphoonForecastSite',
    # backend='amqp',
    broker=BROKER_URL,
    # CELERY_ROUTES={
    #     'worker.test1': {'queue': 'test1'}
    # },
)
app.conf.update(
    CELERY_TASK_SERIALIZER=CELERY_TASK_SERIALIZER,
    CELERY_RESULT_SERIALIZER=CELERY_RESULT_SERIALIZER,
    CELERY_IGNORE_RESULT=True,
    CELERYD_PREFETCH_MULTIPLIER=10,
    CELERYD_MAX_TASKS_PER_CHILD=200,
    CELERY_ACCEPT_CONTENT=CELERY_ACCEPT_CONTENT
)
# app.config_from_object('django.conf:settings', namespace='CELERY')
# # 自动从所有已注册的django app中加载任务
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# app.autodiscover_tasks()
