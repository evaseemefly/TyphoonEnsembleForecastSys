from django.db import models
from django.utils.timezone import now
# 同项目的其他组件
# from typhoon.models import IDelModel, IIdModel, IModel
from common.imodels import IDelModel, IIdModel, IModel, ITimeStamp, ITimeStamp
from util.const import DEFAULT_FK, UNLESS_INDEX, DEFAULT_CODE, ABS_KEY, DEFAULT_NULL_VAL


# Create your models here.


class CaseStatus(IModel, IDelModel, IIdModel):
    celery_id = models.CharField(default=DEFAULT_NULL_VAL, max_length=100)
    case_state = models.IntegerField(default=0)
    case_rate = models.IntegerField(default=0)
    is_lock = models.BooleanField(default=False)

    class Meta:
        db_table = 'Task_CaseStatus'
