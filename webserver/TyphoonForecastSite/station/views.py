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

DEFAULT_PAGE_INDEX = MY_PAGINATOR.get('PAGE_INDEX')
DEFAULT_PAGE_COUNT = MY_PAGINATOR.get('PAGE_COUNT')


class StationListBaseView(APIView):
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


class StationListView(StationListBaseView):
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
        stations: List[StationInfoModel] = self.get_all_station()
        stations_ids: List[int] = [temp.id for temp in stations]

        if pg_id != DEFAULT_NULL_KEY:
            # query = StationForecastRealDataModel.objects.filter(
            #     gp_id=pg_id) if pg_id != DEFAULT_NULL_KEY else StationForecastRealDataModel.objects
            # query = query.filter(forecast_dt=forecast_dt)
            query = self.get_station_complex(pg_id, forecast_dt)
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
