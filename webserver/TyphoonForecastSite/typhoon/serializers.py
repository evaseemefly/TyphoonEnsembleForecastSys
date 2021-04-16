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