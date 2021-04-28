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
from .models import StationForecastRealDataModel, StationInfoModel
from .serializers import StationForecastRealDataSerializer, StationForecastRealDataComplexSerializer
# 公共的
from TyphoonForecastSite.settings import MY_PAGINATOR
from util.const import DEFAULT_NULL_KEY, UNLESS_TY_CODE
from common.view_base import BaseView

DEFAULT_PAGE_INDEX = MY_PAGINATOR.get('PAGE_INDEX')
DEFAULT_PAGE_COUNT = MY_PAGINATOR.get('PAGE_COUNT')


class StationListBaseView(BaseView, APIView):
    def get_all_station(self) -> List[StationInfoModel]:
        """
            获取全部的 非 is_del + is_abs 的station
        @return:
        """
        query: List[StationInfoModel] = StationInfoModel.objects.filter(is_abs=False, is_del=False)
        return query

    def get_station_complex(self, gp_id: int, forecast_dt: str) -> {}:
        # gp_id = 1
        # forecast_index = 1
        # forecast_dt_str:str=datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        # 'SELECT station_forecast_realdata.id, station_forecast_realdata.ty_code,station_forecast_realdata.forecast_dt,station_forecast_realdata.forecast_index,station_forecast_realdata.surge, station_info.name, station_info.lat, station_info.lon FROM  station_forecast_realdata JOIN station_info ON station_forecast_realdata.station_code = station_info.code',
        sql_str: str = f'SELECT station_forecast_realdata.id,station_forecast_realdata.gp_id,station_forecast_realdata.ty_code,station_forecast_realdata.forecast_dt,station_forecast_realdata.forecast_index,station_forecast_realdata.surge,station_info.name,station_info.lat,station_info.lon FROM station_forecast_realdata JOIN station_info ON station_forecast_realdata.station_code = station_info.code WHERE station_forecast_realdata.gp_id= {gp_id} AND station_forecast_realdata.forecast_dt="{forecast_dt}"'
        query = StationForecastRealDataModel.objects.raw(sql_str,
                                                         translations={'ty_code': 'ty_code',
                                                                       'forecast_dt': 'forecast_dt',
                                                                       'forecast_index': 'forecast_index',
                                                                       'surge': 'surge', 'name': 'name', 'lat': 'lat',
                                                                       'lon': 'lon'})
        return query

    def get_relation_station(self, gp_id: int, forecast_dt_str: str) -> {}:
        forecast_dt: datetime = arrow.get(forecast_dt_str).datetime
        # query = StationForecastRealDataModel.objects.filter(gp_id=gp_id)
        # TODO:[*] 21-04-27 最后发现此种方式可行
        # select 就相当于是 sql 中的 SELECT 语句
        # tables 相当于 sql 中的 FROM
        # where 相当于 sql 中的 WHERE
        query = StationForecastRealDataModel.objects.filter(gp_id=gp_id, forecast_dt=forecast_dt).extra(
            select={'station_code': 'station_forecast_realdata.station_code', 'lat': 'station_info.lat',
                    'lon': 'station_info.lon', 'name': 'station_info.name'},
            tables=['station_forecast_realdata', 'station_info'],
            where=['station_forecast_realdata.station_code=station_info.code'])
        return query


class StationListView(StationListBaseView):
    def get(self, request: Request) -> Response:
        """
            根据 group_ id 与 forecast_dt 获取 对应的台风实时数据
            # TODO:[*] 21-04-28 此处缺少对参数的判断
        @param request:
        @return:
        """

        is_paged = bool(int(request.GET.get('is_paged', '0')))
        gp_id: int = int(request.GET.get('gp_id', str(DEFAULT_NULL_KEY)))
        forecast_dt_str: datetime = request.GET.get('forecast_dt')
        page_index = request.GET.get('page_index', str(DEFAULT_PAGE_INDEX))
        page_count = DEFAULT_PAGE_COUNT
        query: List[StationForecastRealDataModel] = []
        stations: List[StationInfoModel] = self.get_all_station()
        stations_ids: List[int] = [temp.id for temp in stations]
        if gp_id != DEFAULT_NULL_KEY:
            # query = StationForecastRealDataModel.objects.filter(
            #     gp_id=pg_id) if pg_id != DEFAULT_NULL_KEY else StationForecastRealDataModel.objects
            # query = query.filter(forecast_dt=forecast_dt)
            # 方式1：实现跨表拼接查询，使用拼接 sql 的方式
            # query = self.get_station_complex(pg_id, forecast_dt_str)
            # 方式2: 使用extra 的方式使用伪sql 代码实现 跨表拼接查询
            query = self.get_relation_station(gp_id=gp_id, forecast_dt_str=forecast_dt_str)
            # 测试一下关联查询
            # res = query.union(stations)
            if is_paged:
                paginator = Paginator(query, page_count)
                contacts = paginator.get_page(page_index)
            try:
                # {AttributeError}Got AttributeError when attempting to get a value for field `station_code` on serializer `StationForecastRealDataComplexSerializer`.
                # The serializer field might be named incorrectly and not match any attribute or key on the `StationInfoModel` instance.
                # Original exception text was: 'StationInfoModel' object has no attribute 'station_code'.
                self.json_data = StationForecastRealDataComplexSerializer(contacts if is_paged else query[:],
                                                                          many=True).data
                self._status = 200
            except Exception as ex:
                self.json = ex.args
        return Response(self.json_data, status=self._status)
