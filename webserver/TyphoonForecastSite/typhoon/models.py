from django.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.utils.timezone import now

# ----
from util.const import DEFAULT_FK, UNLESS_INDEX, DEFAULT_CODE


# Create your models here.
class IIdModel(models.Model):
    id = models.AutoField(primary_key=True)

    class Meta:
        abstract = True


class IDelModel(models.Model):
    is_del = models.BooleanField(default=False)

    class Meta:
        abstract = True


class IModel(models.Model):
    """
        model 抽象父类，主要包含 创建及修改时间
    """

    gmt_created = models.DateTimeField(default=now)
    gmt_modified = models.DateTimeField(default=now)

    class Meta:
        abstract = True


class TyphoonForecastRealDataModel(IIdModel, IDelModel, IModel):
    """
        台风逐时预报信息
    """

    ty_id = models.IntegerField(default=DEFAULT_FK)
    gp_id = models.IntegerField(default=DEFAULT_FK)
    forecast_dt = models.DateTimeField(default=now)
    forecast_index = models.IntegerField(default=UNLESS_INDEX)
    # coords = Column(Geometry('POINT'))
    lat = models.FloatField()
    lon = models.FloatField()
    bp = models.FloatField()
    gale_radius = models.FloatField()

    class Meta:
        db_table = 'typhoon_forecast_realdata'


class TyphoonForecastDetailModel(IIdModel, IDelModel, IModel):
    code = models.CharField(max_length=200)
    organ_code = models.IntegerField(default=UNLESS_INDEX)
    gmt_start = models.DateTimeField(default=now)
    gmt_end = models.DateTimeField(default=now)
    forecast_source = models.IntegerField(default=UNLESS_INDEX)
    is_forecast = models.BooleanField(default=True)

    class Meta:
        db_table = 'typhoon_forecast_detailinfo'


class TyphoonGroupPathModel(IIdModel, IDelModel, IModel):
    ty_id = models.IntegerField(default=DEFAULT_FK)
    ty_code = models.CharField(max_length=200)
    file_name = models.CharField(max_length=200)
    relative_path = models.CharField(max_length=500)
    area = models.IntegerField(default=UNLESS_INDEX)
    timestamp = models.CharField(max_length=100)
    ty_path_type = models.CharField(max_length=3, default=DEFAULT_CODE)
    ty_path_marking = models.IntegerField()
    bp = models.FloatField()
    is_bp_increase = models.BooleanField(default=False)

    class Meta:
        db_table = 'typhoon_forecast_grouppath'


class TyphoonComplexGroupRealDataModel(models.Model):
    ty_id = models.IntegerField(default=DEFAULT_FK)
    ty_code = models.CharField(max_length=200)
    area = models.IntegerField(default=UNLESS_INDEX)
    timestamp = models.CharField(max_length=100)
    ty_path_type = models.CharField(max_length=3, default=DEFAULT_CODE)
    ty_path_marking = models.IntegerField()
    bp = models.FloatField()
    is_bp_increase = models.BooleanField(default=False)
    # list_realdata=models.ListField(TyphoonForecastRealDataModel)
    class Meta:
        abstract = True