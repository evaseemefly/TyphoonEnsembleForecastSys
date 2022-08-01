from django.db import models
from django.utils.timezone import now
# 同项目的其他组件
# from typhoon.models import IDelModel, IIdModel, IModel
from common.imodels import IDelModel, IIdModel, IModel, ITimeStamp, ITimeStamp
from util.const import DEFAULT_FK, UNLESS_INDEX, DEFAULT_CODE, ABS_KEY


# Create your models here.

class StationInfoModel(IModel, IDelModel, IIdModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    desc = models.CharField(max_length=500, null=True)
    pid = models.IntegerField(default=ABS_KEY)  # 添加的所属父级id
    is_abs = models.BooleanField(default=False)  # 是否为抽象对象(抽象对象不显示)
    base_level_diff = models.FloatField(null=True)
    d85 = models.IntegerField()
    is_in_use = models.BooleanField(default=True)  # 是否为使用中的站点(部分海洋站没有四色警戒潮位，不作为使用站点)

    class Meta:
        db_table = 'station_info'


class StationForecastRealDataSharedMdoel(IIdModel, IDelModel, IModel, ITimeStamp):
    SHARED_TABLE_BASE_NAME = 'station_forecast_realdata'
    """
        + 22-05-24 尝试加入分表功能
                   大体逻辑:
                            根据 ty_code 进行分表
                            表名: station_forecast_realdata_2017
                                 station_forecast_realdata_{ty_code}
    """
    ty_code = models.CharField(max_length=200)
    gp_id = models.IntegerField(default=DEFAULT_FK)
    station_code = models.CharField(max_length=10, default=DEFAULT_CODE)
    forecast_dt = models.DateTimeField(default=now)
    forecast_index = models.IntegerField(default=UNLESS_INDEX)
    surge = models.FloatField()
    timestamp = models.CharField(max_length=100, default='2021010416')  # + 21-05-11 新加入的时间戳字段

    @classmethod
    def get_sharding_tb_name(cls, ty_code=None):
        db_table = f'{cls.SHARED_TABLE_BASE_NAME}_{ty_code}'
        return db_table

    @classmethod
    def get_sharding_model(cls, ty_code=None):
        class Meta:
            db_table = f'{cls.SHARED_TABLE_BASE_NAME}_{ty_code}'

        attrs = {
            '__module__': cls.__module__,
            '__doc__': f'station_code:{ty_code}',
            'Meta': Meta
        }
        return type(str('StationForecastRealDataModel'), (cls,), attrs)

    class Meta:
        abstract = True


class StationForecastRealDataModel(IIdModel, IDelModel, IModel, ITimeStamp):
    # ty_id = models.IntegerField(default=DEFAULT_FK)
    ty_code = models.CharField(max_length=200)
    gp_id = models.IntegerField(default=DEFAULT_FK)
    # 需要手动与 StationInfoModel 建立关联，但不加上外键
    # station_code = models.ForeignKey(StationInfoModel, null=True, on_delete=models.SET_NULL,
    #                                  related_name='station_code', db_column='station_code',
    #                                  db_constraint=False)
    station_code = models.CharField(max_length=10, default=DEFAULT_CODE)
    # ERRORS:
    # station.StationForecastRealDataModel.station_code: (fields.E302) Reverse accessor for 'StationForecastRealDataModel.station_code' clashes with field name 'StationInfoModel.code'.
    # 	HINT: Rename field 'StationInfoModel.code', or add/change a related_name argument to the definition for field 'StationForecastRealDataModel.station_code'.
    # station_code = models.ManyToManyField(StationInfoModel,related_name='code')
    # lat = models.FloatField()
    # lon = models.FloatField()
    forecast_dt = models.DateTimeField(default=now)
    forecast_index = models.IntegerField(default=UNLESS_INDEX)
    surge = models.FloatField()
    timestamp = models.CharField(max_length=100, default='2021010416')  # + 21-05-11 新加入的时间戳字段

    # station_info = models.OneToOneField(StationInfoModel, on_delete=models.CASCADE)

    # bp=models.FloatField()

    class Meta:
        db_table = 'station_forecast_realdata'


class StationAstronomicTideRealDataModel(IIdModel, IDelModel, IModel):
    '''
        + 21-08-24 天文潮位表
    '''
    station_code = models.CharField(max_length=10, default=DEFAULT_CODE)
    forecast_dt = models.DateTimeField(default=now)
    surge = models.FloatField()

    class Meta:
        db_table = 'station_astronomictidee _realdata'


class StationAlertTideModel(IIdModel, IDelModel, IModel):
    """
        + 21-08-25 警戒潮位表
    """
    station_code = models.CharField(max_length=10, default=DEFAULT_CODE)
    tide = models.FloatField()
    alert = models.IntegerField()


class StationStatisticsModel(IIdModel, IDelModel, IModel):
    """
        + 21-10-27 海洋站分位数表
                   主要用来保存海洋站各统计 分位数
    """
    quarter_val = models.FloatField()  # 1/4 分位数
    three_quarters_val = models.FloatField()  # 3/4 分位数
    median_val = models.FloatField()  # 中位数
    max_val = models.FloatField()  # 最大值
    min_val = models.FloatField()  # 最小值
    ty_code = models.CharField(max_length=200)
    station_code = models.CharField(max_length=10, default=DEFAULT_CODE)
    forecast_dt = models.DateTimeField(default=now)
    forecast_index = models.IntegerField(default=UNLESS_INDEX)
    timestamp = models.CharField(max_length=100, default='2021010416')  # + 21-05-11 新加入的时间戳字段

    class Meta:
        db_table = 'station_quantile_realdata'


# class StationComplexModel(IIdModel):
#     ty_code = models.CharField(max_length=200)
#     gp_id = models.IntegerField(default=DEFAULT_FK)
#     station_code = models.CharField(max_length=10, default=DEFAULT_CODE)
#     # lat = models.FloatField()
#     # lon = models.FloatField()
#     forecast_dt = models.DateTimeField(default=now)
#     forecast_index = models.IntegerField(default=UNLESS_INDEX)
#     surge = models.FloatField()
#     name = models.CharField(max_length=200)
#     code = models.CharField(max_length=50)
#     lat = models.FloatField(null=True)
#     lon = models.FloatField(null=True)
#
#     class Meta:
#         db_table = 'station_info'
# abstract = True

class TideDataModel(IIdModel):
    """
        + 22-07-31 每日的两个或一个高潮位表
    """
    station_code = models.CharField(max_length=10)
    forecast_dt = models.DateTimeField(default=now)
    surge = models.FloatField()
    tide_type = models.IntegerField(default=UNLESS_INDEX)

    class Meta:
        db_table = 'tide_data_daily'
