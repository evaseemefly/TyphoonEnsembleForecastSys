from django.shortcuts import render
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
from django.db.models import QuerySet
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)
import arrow

from .views_base import RasterBaseView, RasterMaxBaseView
from util.const import DEFAULT_NULL_KEY, UNLESS_INDEX
from util.enum import LayerTypeEnum
from util.customer_exception import NoneError


# Create your views here.

class GeoTiffView(RasterBaseView):
    def get(self, request: Request) -> Response:
        id: int = int(request.GET.get('id')) if request.GET.get('id', None) else DEFAULT_NULL_KEY
        ty_code: str = request.GET.get('ty_code', None)
        ty_timestamp_str: str = request.GET.get('ty_timestamp', None)
        forecast_dt: datetime = request.GET.get('forecast_dt', None)
        # ty_timestamp: datetime = arrow.get(ty_timestamp_str).datetime
        try:
            self.json_data = self.get_tif_url(request, id=id, ty_code=ty_code, timestamp=ty_timestamp_str,
                                              forecast_dt=forecast_dt)
            self._status = 200
        except NoneError as noneErr:
            self.json_data = noneErr.args
        except  Exception as e:
            self.json_data = e.args
        return Response(self.json_data, status=self._status)


class GeoTiffMaxSurgeView(RasterBaseView):
    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', None)
        ty_timestamp_str: str = request.GET.get('ty_timestamp', None)
        # query: QuerySet = self._query_base_tif(ty_code=ty_code, ty_timestamp=ty_timestamp_str)
        # query = query.filter(coverage_type=LayerTypeEnum.SURGE_MAX_COVERAGE.value)
        # if len(query)>0:
        #     query.first().
        try:
            url_fullpath: str = self.get_tif_url(request, ty_code=ty_code, timestamp=ty_timestamp_str,
                                                 coverage_type=LayerTypeEnum.SURGE_MAX_TIF)
            self.json_data = url_fullpath
            self._status = 200
        except NoneError as noneErr:
            self.json_data = noneErr.args
        except  Exception as e:
            self.json_data = e.args
        return Response(self.json_data, status=self._status)


class GeoTiffFieldSurgeView(RasterBaseView):
    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', None)
        ty_timestamp_str: str = request.GET.get('ty_timestamp', None)
        COVERAGE_TYPE_VAL: int = LayerTypeEnum.SURGE_FIELD_TIF.value
        forecast_dt: datetime = request.GET.get('forecast_dt', None)
        try:
            tif_url = self.get_tif_url(request, ty_code=ty_code, timestamp=ty_timestamp_str,
                                       coverage_type=LayerTypeEnum.SURGE_FIELD_TIF, forecast_dt=forecast_dt)
            self.json_data = tif_url
            self._status = 200
        except NoneError as noneErr:
            self.json_data = noneErr.args
        except  Exception as e:
            self.json_data = e.args
        return Response(self.json_data, status=self._status)


class GeoTiffProSurgeView(RasterBaseView):
    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', None)
        ty_timestamp_str: str = request.GET.get('ty_timestamp', None)
        pro: float = float(request.GET.get('pro', None))
        coverage_type = int(request.GET.get('coverage_type', str(UNLESS_INDEX)))
        try:
            tif_url = self.get_tif_url(request, ty_code=ty_code, timestamp=ty_timestamp_str,
                                       coverage_type=coverage_type, pro=pro)
            self.json_data = tif_url
            self._status = 200
        except NoneError as noneErr:
            self.json_data = noneErr.args
        except  Exception as e:
            self.json_data = e.args
        return Response(self.json_data, status=self._status)


class GetTiffMaxSurgeRangeView(RasterMaxBaseView):
    """
        + 22-03-17 新加入的获取 geotiff 最大增水场的极值范围
    """

    def get(self, request: Request) -> Response:
        """
            + 22-03-17 获取当前过程的 最大增水场的极值范围
        """
        ty_code: str = request.GET.get('ty_code', None)
        ty_timestamp_str: str = request.GET.get('ty_timestamp', None)
        try:
            query = self.get_max_surge_coverage(ty_code, ty_timestamp_str)
            res = {'max': query.surge_max, 'min': query.surge_min}
            self.json_data = res
            self._status = 200
        except Exception as ex:
            self.json_data = ex.args
        return Response(self.json_data, status=self._status)

        pass
