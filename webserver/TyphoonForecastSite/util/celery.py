from celery import Celery

app = Celery('CeleryTest')
# settings内关于celery的设置，以CELERY_ 格式书写
app.config_from_object('conf:settings', namespace='CELERY')

# app.conf.update(
#     CELERY_TASK_SERIALIZER=CELERY_TASK_SERIALIZER,
#     CELERY_RESULT_SERIALIZER=CELERY_RESULT_SERIALIZER,
#     CELERY_IGNORE_RESULT=True,
#     CELERYD_PREFETCH_MULTIPLIER=10,
#     CELERYD_MAX_TASKS_PER_CHILD=200,
#     CELERY_ACCEPT_CONTENT=CELERY_ACCEPT_CONTENT,
#     CELERY_IMPORTS=('task.tasks', 'case.case')
# )