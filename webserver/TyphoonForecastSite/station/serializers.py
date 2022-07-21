from rest_framework import serializers


class StationForecastRealDataSerializer(serializers.Serializer):
    ty_code = serializers.CharField()
    gp_id = serializers.IntegerField()
    station_code = serializers.CharField()
    forecast_index = serializers.IntegerField()
    forecast_dt = serializers.DateTimeField(required=False)
    # surge = serializers.FloatField()
    surge = serializers.DecimalField(max_digits=None, decimal_places=2)


class StationForecastRealDataMiniSerializer(serializers.Serializer):
    forecast_index = serializers.IntegerField()
    surge = serializers.DecimalField(max_digits=None, decimal_places=2)


class StationAstronomicTideRealDataSerializer(serializers.Serializer):
    station_code = serializers.CharField()
    forecast_dt = serializers.DateTimeField()
    surge = serializers.FloatField()


class StationForecastRealDataComplexSerializer(serializers.Serializer):
    ty_code = serializers.CharField(required=False)
    gp_id = serializers.IntegerField(required=False)
    station_code = serializers.CharField()
    forecast_index = serializers.IntegerField(required=False)
    forecast_dt = serializers.DateTimeField(required=False)
    surge = serializers.FloatField()
    name = serializers.CharField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()


class StationForecastRealDataRangeSerializer(serializers.Serializer):
    surge_max = serializers.FloatField()
    surge_min = serializers.FloatField(required=False)
    base_level_diff = serializers.FloatField(required=False)
    station_code = serializers.CharField()


class StationForecastRealDataRangeComplexSerializer(serializers.Serializer):
    """
        + 21-05-26 海洋展潮位数据 混合 序列化器
    """
    forecast_dt = serializers.DateTimeField()
    surge = serializers.FloatField()
    surge_max = serializers.FloatField()
    surge_min = serializers.FloatField()


class StationAlertSerializer(serializers.Serializer):
    """
        + 21-05-26 海洋展潮位数据 混合 序列化器
    """
    station_code = serializers.CharField()
    tide = serializers.FloatField()
    alert = serializers.IntegerField()


class StationForecastRealDataByGroupSerializer(serializers.Serializer):
    gp_id = serializers.IntegerField()
    list_realdata = StationForecastRealDataMiniSerializer(many=True)
    # list_realdata=serializers.ListSerializer


class StationForecastRealDataMixin(StationForecastRealDataComplexSerializer, StationForecastRealDataRangeSerializer):
    pass


class StationInfoSerializer(serializers.Serializer):
    """
        站点基础静态信息(经纬度，name等)
    """
    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()


class StationStatisticsSerializer(serializers.Serializer):
    ty_code = serializers.CharField()
    station_code = serializers.CharField()
    forecast_index = serializers.IntegerField()
    forecast_dt = serializers.DateTimeField()
    quarter_val = serializers.FloatField()
    three_quarters_val = serializers.FloatField()
    median_val = serializers.FloatField()
    max_val = serializers.FloatField()
    min_val = serializers.FloatField(required=False)
