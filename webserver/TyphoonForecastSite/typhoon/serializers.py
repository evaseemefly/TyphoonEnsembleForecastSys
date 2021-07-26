from rest_framework import serializers


# from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeoFeatureModelListSerializer, GeoModelSerializer, \
#     GeometryField

class TyphoonForecastDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    organ_code = serializers.CharField()
    gmt_start = serializers.DateTimeField()
    gmt_end = serializers.DateTimeField()
    is_forecast = serializers.BooleanField()


class TyphoonGroupPathSerializer(serializers.Serializer):
    ty_id = serializers.IntegerField()
    ty_code = serializers.CharField()
    area = serializers.IntegerField()
    ty_path_type = serializers.CharField()
    ty_path_marking = serializers.IntegerField()
    bp = serializers.FloatField()
    is_bp_increase = serializers.BooleanField()


class TyphoonDistGroupPathMidSerializer(serializers.Serializer):
    """
        + 21-07-25:
            对应 typhoon/mid_models -> TyphoonGroupDistMidModel
    """
    ty_id = serializers.IntegerField()
    ty_code = serializers.CharField()
    timestamp = serializers.CharField()
    gmt_created = serializers.DateTimeField()
    forecast_start = serializers.DateTimeField()
    forecast_end = serializers.DateTimeField()


class TyphoonForecastRealDataSerializer(serializers.Serializer):
    ty_id = serializers.IntegerField()
    gp_id = serializers.IntegerField()
    forecast_dt = serializers.DateTimeField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    bp = serializers.FloatField()
    gale_radius = serializers.FloatField()


class TyphoonComplexGroupRealDataModelSerializer(serializers.Serializer):
    ty_id = serializers.IntegerField()
    ty_code = serializers.CharField()
    area = serializers.IntegerField()
    ty_path_type = serializers.CharField()
    ty_path_marking = serializers.IntegerField()
    bp = serializers.FloatField()
    is_bp_increase = serializers.BooleanField()
    list_realdata = serializers.ListField(child=TyphoonForecastRealDataSerializer())
