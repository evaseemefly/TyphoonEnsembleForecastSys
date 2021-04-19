from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)
from rest_framework.response import Response


class BaseView(APIView):
    """
        + 21-04-19 父类，默认加入了几个默认字段
    """
    _status = 500
    json_data = None
