import os
from celery import Celery, platforms
from django.conf import settings
from task.settings import BROKER_URL, CELERY_RESULT_BACKEND, CELERY_TASK_SERIALIZER, CELERY_RESULT_SERIALIZER, \
    CELERY_TASK_RESULT_EXPIRES, CELERY_ACCEPT_CONTENT

# 为celery设置环境变量 django -> settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TyphoonForecastSite.settings')
app = Celery(
    # backend='amqp',
    broker=BROKER_URL,
    CELERY_ROUTES={
        'worker.test1': {'queue': 'test1'}
    },
)

# ERROR； ValueError: not enough values to unpack (expected 3, got 0)
# TODO:[*] celery 3.1 开始可以通过如下的方式获取task的id
@app.task(bind=True)
def my_task(*args):
    print('测试耗时任务')
    print(f'传入的参数为:{args}')
    # print(f'{self}')
    # if hasattr(msg, 'username'):
    #     print(f'self.request.id:{self.request.id}|{msg.username}')
    print(f'开始调用oil job')
    # print(sys.path)
    # main.do_job()
    # time.sleep(5)
    print('耗时任务结束')
    print('--------------')
