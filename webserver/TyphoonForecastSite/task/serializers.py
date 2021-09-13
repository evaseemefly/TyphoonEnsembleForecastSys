from rest_framework import serializers


class CaseStatusModelSerializer(serializers.Serializer):
    celery_id = serializers.CharField()
    case_state = serializers.IntegerField()
    case_rate = serializers.IntegerField()
    # is_lock = serializers.BooleanField()
    # id = serializers.IntegerField()
    gmt_created = serializers.DateTimeField()
    # gmt_modified = serializers.DateTimeField()
