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


class StationForecastRealDataMixin(StationForecastRealDataComplexSerializer, StationForecastRealDataRangeSerializer):
    pass
