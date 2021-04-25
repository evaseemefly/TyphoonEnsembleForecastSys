from django.shortcuts import render
import pathlib
from datetime import datetime
from os import path
from typing import List

import arrow
from django.shortcuts import render
from django.core.serializers import serialize
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)

# --
# 本项目的
from .models import StationForecastRealDataModel
from .serializers import StationForecastRealDataSerializer
# 公共的
from TyphoonForecastSite.settings import MY_PAGINATOR
from util.const import DEFAULT_NULL_KEY, UNLESS_TY_CODE

DEFAULT_PAGE_INDEX = MY_PAGINATOR.get('PAGE_INDEX')
DEFAULT_PAGE_COUNT = MY_PAGINATOR.get('PAGE_COUNT')


class StationListView(APIView):
    def get(self, request: Request) -> Response:
        """
            根据 group_ id 获取 对应的台风实时数据
        @param request:
        @return:
        """

        is_paged = bool(int(request.GET.get('is_paged', '0')))
        pg_id: int = int(request.GET.get('pg_id'))
        forecast_dt: datetime = request.GET.get('forecast_dt')
        page_index = request.GET.get('page_index', str(DEFAULT_PAGE_INDEX))
        page_count = DEFAULT_PAGE_COUNT
        query: List[StationForecastRealDataModel] = []
        if pg_id != DEFAULT_NULL_KEY:
            query = StationForecastRealDataModel.objects.filter(
                gp_id=pg_id) if pg_id != DEFAULT_NULL_KEY else StationForecastRealDataModel.objects
            query = query.filter(forecast_dt=forecast_dt)
            if is_paged:
                paginator = Paginator(query, page_count)
                contacts = paginator.get_page(page_index)
            try:
                self.json_data = StationForecastRealDataSerializer(contacts if is_paged else query, many=True).data
                self._status = 200
            except Exception as ex:
                self.json = ex.args
        return Response(self.json_data, status=self._status)
