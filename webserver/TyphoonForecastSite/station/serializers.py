from rest_framework import serializers


class StationForecastRealDataSerializer(serializers.Serializer):
    ty_code = serializers.CharField()
    gp_id = serializers.IntegerField()
    station_code = serializers.CharField()
    forecast_index = serializers.IntegerField()
    forecast_dt = serializers.DateTimeField()
    surge = serializers.FloatField()


class StationForecastRealDataComplexSerializer(serializers.Serializer):
    ty_code = serializers.CharField()
    gp_id = serializers.IntegerField()
    station_code = serializers.CharField()
    forecast_index = serializers.IntegerField()
    forecast_dt = serializers.DateTimeField()
    surge = serializers.FloatField()
    name = serializers.CharField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()


class StationForecastRealDataRangeSerializer(serializers.Serializer):
    surge_max = serializers.FloatField()
    surge_min = serializers.FloatField()
    station_code = serializers.CharField()


class StationForecastRealDataRangeComplexSerializer(serializers.Serializer):
    """
        + 21-05-26 海洋展潮位数据 混合 序列化器
    """
    forecast_dt = serializers.DateTimeField()
    surge = serializers.FloatField()
    surge_max = serializers.FloatField()
    surge_min = serializers.FloatField()


class StationForecastRealDataMixin(StationForecastRealDataComplexSerializer, StationForecastRealDataRangeSerializer):
    pass
