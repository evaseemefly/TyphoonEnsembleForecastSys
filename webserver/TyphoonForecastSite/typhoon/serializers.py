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


class TyphoonContainsCodeAndStSerializer(serializers.Serializer):
    ty_code = serializers.CharField()
    timestamp = serializers.CharField()


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
    # list_realdata = serializers.ListField(child=TyphoonForecastRealDataSerializer())
    list_realdata = TyphoonForecastRealDataSerializer(many=True, read_only=True)

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('list_realdata')
        return queryset


class TyphoonComplexGroupRealDataNewModelSerializer(serializers.Serializer):
    """
        + 21-10-10 新加入的序列化器 用于 序列化 关联查询
        tb:typhoon_forecast_realdata + tb:typhoon_forecast_grouppath
        拼接后的结果
    """
    timestamp = serializers.CharField()
    forecast_dt = serializers.DateTimeField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    bp = serializers.FloatField()
    gale_radius = serializers.FloatField()
    ty_path_type = serializers.CharField()
    ty_path_marking = serializers.IntegerField()
    is_bp_increase = serializers.BooleanField()


class TyphoonComplexGroupRealDataDictModelSerializer(serializers.Serializer):
    """
        + 21-10-10 新加入的序列化器 用于 序列化 关联查询
        tb:typhoon_forecast_realdata + tb:typhoon_forecast_grouppath
        拼接后的结果
    """
    timestamp = serializers.CharField()
    forecast_dt = serializers.DateTimeField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    realdata_bp = serializers.FloatField()
    gale_radius = serializers.FloatField()
    ty_path_type = serializers.CharField()
    ty_path_marking = serializers.IntegerField()
    is_bp_increase = serializers.BooleanField()


class TyphoonComplexGroupDictMidSerializer(serializers.Serializer):
    gp_id = serializers.IntegerField()
    group_bp = serializers.FloatField()
    # is_bp_increase=serializers.BooleanField()
    # gale_radius = serializers.FloatField()
    ty_path_type = serializers.CharField()
    ty_path_marking = serializers.IntegerField()
    is_bp_increase = serializers.BooleanField()
    list_realdata = TyphoonComplexGroupRealDataDictModelSerializer(many=True)


class TyRealDataMidSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    bp = serializers.FloatField()
    ts = serializers.IntegerField()
    ty_type = serializers.CharField()


class TyPathMidSerializer(serializers.Serializer):
    ty_id = serializers.IntegerField()
    ty_code = serializers.CharField()
    ty_name_en = serializers.CharField()
    ty_name_ch = serializers.CharField()
    ty_path_list = TyRealDataMidSerializer(many=True)
