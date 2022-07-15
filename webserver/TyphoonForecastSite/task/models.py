from django.db import models
from django.utils.timezone import now
# 同项目的其他组件
# from typhoon.models import IDelModel, IIdModel, IModel
from common.imodels import IDelModel, IIdModel, IModel, ITimeStamp, ITimeStamp
from util.const import DEFAULT_FK, UNLESS_INDEX, DEFAULT_CODE, ABS_KEY, DEFAULT_NULL_VAL, UNLESS_CELERY_ID, \
    DEFAULT_TIMTSTAMP_STR


# Create your models here.


class CaseStatusModel(IModel, IDelModel, IIdModel):
    celery_id = models.CharField(default=UNLESS_CELERY_ID, max_length=100)
    case_state = models.IntegerField(default=0)
    case_rate = models.IntegerField(default=0)
    is_lock = models.BooleanField(default=False)

    class Meta:
        db_table = 'task_casestatus'


class CaseInstanceModel(IModel, IDelModel, IIdModel):
    """
        记录作业的详情 model
    """
    # celery_id = models.CharField(default=UNLESS_CELERY_ID, max_length=100)
    ty_code = models.CharField(default=DEFAULT_CODE, max_length=100)
    gmt_commit = models.DateTimeField(default=now)
    member_num = models.IntegerField(default=-1)  # 成员数
    max_wind_radius_dif = models.IntegerField(default=-9999)  # 大风半径增减值(可能出现负数)
    json_field = models.JSONField(default={})
    timestamp = models.CharField(default=DEFAULT_TIMTSTAMP_STR, max_length=100)  # TODO:[-] 21-12-02 加入了时间戳
    area = models.IntegerField(default=510)

    # hours = models.IntegerField(default=-1)
    # radius = models.IntegerField(default=-9999)

    class Meta:
        db_table = 'task_caseinstance'
