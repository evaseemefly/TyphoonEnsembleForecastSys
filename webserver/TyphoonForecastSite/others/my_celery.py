import os
from celery import Celery
from others.settings import BROKER_URL
from TyphoonForecastSite import settings

# 为celery设置环境变量 django -> settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TyphoonForecastSite.settings')
app = Celery(
    # backend='amqp',
    broker=BROKER_URL,
    CELERY_ROUTES={
        'worker.test1': {'queue': 'test1'}
    },
)

# 自动从所有已注册的django app中加载任务
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
