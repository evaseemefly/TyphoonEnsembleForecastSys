from django.shortcuts import render
import pathlib
from datetime import datetime
from os import path
from typing import List

import arrow
from django.shortcuts import render
from django.core.serializers import serialize
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)
from rest_framework.response import Response
from rest_framework.request import Request

# -- 本项目
from .models import TyphoonForecastDetailModel
from .serializers import TyphoonForecastDetailSerializer


# Create your views here.

class TyDetailModelView(APIView):
    _status = 500
    json_data = None

    # @request_need_factors_wrapper(['ids'], 'GET')
    def get(self, request):
        # 获取 ids
        forecast_dt = request.GET.get('forecast_dt', None)
        query: List[TyphoonForecastDetailModel] = []
        if forecast_dt:
            query = TyphoonForecastDetailModel.objects.filter(gmt_start=forecast_dt)

        try:
            self.json_data = TyphoonForecastDetailSerializer(query, many=True).data
            self._status = 200
        except Exception as ex:
            json = ex.args

        return Response(self.json_data, status=self._status)
