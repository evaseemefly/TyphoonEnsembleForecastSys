from rest_framework import serializers

class TyExistedStatusSerializer(serializers.Serializer):
    geo_raster_status = serializers.BooleanField()
    station_realdata_staus = serializers.BooleanField()
    ty_group_path_status = serializers.BooleanField()