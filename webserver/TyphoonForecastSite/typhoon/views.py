from django.shortcuts import render
import pathlib
from datetime import datetime
from os import path
from typing import List

import arrow
from django.shortcuts import render
from django.core.serializers import serialize
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)
from rest_framework.response import Response
from rest_framework.request import Request

# -- 本项目
from .view_base import BaseView
from .models import TyphoonForecastDetailModel, TyphoonGroupPathModel, TyphoonForecastRealDataModel
from .serializers import TyphoonForecastDetailSerializer, TyphoonGroupPathSerializer, TyphoonForecastRealDataSerializer
from TyphoonForecastSite.settings import MY_PAGINATOR
from util.const import DEFAULT_NULL_KEY, UNLESS_TY_CODE

DEFAULT_PAGE_INDEX = MY_PAGINATOR.get('PAGE_INDEX')
DEFAULT_PAGE_COUNT = MY_PAGINATOR.get('PAGE_COUNT')


# Create your views here.

class TyDetailModelView(BaseView):
    """
        根据预报时间获取对应的 detailModel 列表
    """

    # _status = 500
    # json_data = None

    # @request_need_factors_wrapper(['ids'], 'GET')
    def get(self, request):
        """

        @param request:
        @return:
        """
        # 获取 ids
        forecast_dt = request.GET.get('forecast_dt', None)
        is_paged = request.GET.get('is_paged', False)
        page_index = request.GET.get('page_index', str(DEFAULT_PAGE_INDEX))
        page_count = DEFAULT_PAGE_COUNT

        query: List[TyphoonForecastDetailModel] = []
        if forecast_dt:
            query = TyphoonForecastDetailModel.objects.filter(gmt_start=forecast_dt)
            if is_paged:
                paginator = Paginator(query, page_count)
                contacts = paginator.get_page(page_index)
        try:
            self.json_data = TyphoonForecastDetailSerializer(contacts if is_paged else query, many=True).data
            self._status = 200
        except Exception as ex:
            self.json = ex.args

        return Response(self.json_data, status=self._status)


class TyGroupPathView(BaseView):
    """

    """

    def get(self, request):
        """
            根据 ty_id 获取 groupPath 列表
        @param request:
        @return:
        """
        # tyDetailModel id
        ty_id: int = int(request.GET.get('ty_id', str(DEFAULT_NULL_KEY)))
        # tyDetailModel code
        ty_code: str = request.GET.get('ty_code', UNLESS_TY_CODE)
        is_paged = bool(int(request.GET.get('is_paged', '0')))
        page_index = request.GET.get('page_index', str(DEFAULT_PAGE_INDEX))
        page_count = DEFAULT_PAGE_COUNT
        query: List[TyphoonGroupPathModel] = []
        if any([ty_id != DEFAULT_NULL_KEY, ty_code != UNLESS_TY_CODE]):
            query = TyphoonGroupPathModel.objects.filter(
                ty_id=ty_id) if ty_id != DEFAULT_NULL_KEY else TyphoonGroupPathModel.objects
            query = query.filter(ty_code=ty_code) if ty_code != UNLESS_TY_CODE else query
            if is_paged:
                paginator = Paginator(query, page_count)
                contacts = paginator.get_page(page_index)
            try:
                self.json_data = TyphoonGroupPathSerializer(contacts if is_paged else query, many=True).data
                self._status = 200
            except Exception as ex:
                self.json = ex.args
        return Response(self.json_data, status=self._status)


class TyRealDataView(BaseView):
    def get(self, request: Request) -> Response:
        """
            根据 group_ id 获取 对应的台风实时数据
        @param request:
        @return:
        """
        groupd_id: int = int(request.GET.get('group_id', str(DEFAULT_NULL_KEY)))
        is_paged = bool(int(request.GET.get('is_paged', '0')))
        page_index = request.GET.get('page_index', str(DEFAULT_PAGE_INDEX))
        page_count = DEFAULT_PAGE_COUNT
        query: List[TyphoonGroupPathModel] = []
        if groupd_id != DEFAULT_NULL_KEY:
            query = TyphoonForecastRealDataModel.objects.filter(
                gp_id=groupd_id) if groupd_id != DEFAULT_NULL_KEY else TyphoonForecastRealDataModel.objects

            if is_paged:
                paginator = Paginator(query, page_count)
                contacts = paginator.get_page(page_index)
            try:
                self.json_data = TyphoonForecastRealDataSerializer(contacts if is_paged else query, many=True).data
                self._status = 200
            except Exception as ex:
                self.json = ex.args
        return Response(self.json_data, status=self._status)
