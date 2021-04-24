from django.db import models
from django.utils.timezone import now
# 同项目的其他组件
from typhoon.models import IDelModel, IIdModel, IModel
from util.const import DEFAULT_FK, UNLESS_INDEX, DEFAULT_CODE


# Create your models here.
class StationForecastRealDataModel(IIdModel, IDelModel, IModel):
    # ty_id = models.IntegerField(default=DEFAULT_FK)
    ty_code = models.CharField(max_length=200)
    gp_id = models.IntegerField(default=DEFAULT_FK)
    station_code = models.CharField(max_length=10, default=DEFAULT_CODE)
    lat = models.FloatField()
    lon = models.FloatField()
    forecast_dt = models.DateTimeField(default=now)
    forecast_index = models.IntegerField(default=UNLESS_INDEX)
    surge = models.FloatField()

    # bp=models.FloatField()

    class Meta:
        db_table = 'station_forecast_realdata'
