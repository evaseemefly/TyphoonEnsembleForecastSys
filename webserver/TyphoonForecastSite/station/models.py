from django.db import models
from django.utils.timezone import now
# 同项目的其他组件
from typhoon.models import IDelModel, IIdModel, IModel
from util.const import DEFAULT_FK, UNLESS_INDEX, DEFAULT_CODE, ABS_KEY


# Create your models here.
class StationForecastRealDataModel(IIdModel, IDelModel, IModel):
    # ty_id = models.IntegerField(default=DEFAULT_FK)
    ty_code = models.CharField(max_length=200)
    gp_id = models.IntegerField(default=DEFAULT_FK)
    station_code = models.CharField(max_length=10, default=DEFAULT_CODE)
    # lat = models.FloatField()
    # lon = models.FloatField()
    forecast_dt = models.DateTimeField(default=now)
    forecast_index = models.IntegerField(default=UNLESS_INDEX)
    surge = models.FloatField()

    # bp=models.FloatField()

    class Meta:
        db_table = 'station_forecast_realdata'


class StationInfoModel(IModel, IDelModel, IIdModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    desc = models.CharField(max_length=500, null=True)
    pid = models.IntegerField(default=ABS_KEY)  # 添加的所属父级id
    is_abs = models.BooleanField(default=False)  # 是否为抽象对象(抽象对象不显示)

    class Meta:
        db_table = 'station_info'
