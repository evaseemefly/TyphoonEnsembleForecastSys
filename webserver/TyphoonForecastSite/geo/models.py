from django.db import models
from django.utils.timezone import now
# 同项目的其他组件
from util.const import DEFAULT_FK, DEFAULT_PRO
from common.imodels import IDelModel, IIdModel, IModel, IFileModel, ITyPathModel, IBpModel, ISpliceModel


# Create your models here.

class CoverageInfoModel(IDelModel, IIdModel, IModel, ITyPathModel, IBpModel, ISpliceModel, IFileModel):
    forecast_area = models.IntegerField(default=DEFAULT_FK)
    coverage_type = models.IntegerField(default=DEFAULT_FK)
    ty_code = models.CharField(max_length=200)
    timestamp = models.CharField(max_length=100)
    is_source = models.BooleanField(default=True)

    class Meta:
        db_table = 'geo_coverageinfo'


class ForecastTifModel(IDelModel, IIdModel, IModel, ITyPathModel, IBpModel, ISpliceModel, IFileModel):
    # gcid = models.IntegerField(default=DEFAULT_FK)
    coverage_type = models.IntegerField(default=DEFAULT_FK)
    ty_code = models.CharField(max_length=200)
    timestamp = models.CharField(max_length=100)
    forecast_dt = models.DateTimeField(default=now)

    class Meta:
        db_table = 'geo_forecast_tif'


class ForecastProTifModel(IDelModel, IIdModel, IModel, ITyPathModel, ISpliceModel, IFileModel):
    coverage_type = models.IntegerField(default=DEFAULT_FK)
    ty_code = models.CharField(max_length=200)
    timestamp = models.CharField(max_length=100)
    pro = models.FloatField(default=DEFAULT_PRO)

    class Meta:
        db_table = 'geo_forecast_pro_tif'
