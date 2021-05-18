from django.shortcuts import render
import pathlib
from datetime import datetime
from os import path
from typing import List

import arrow
from django.shortcuts import render
from django.core.serializers import serialize
from django.db.models import Max, Min
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)

# --
# 本项目的
from .models import StationForecastRealDataModel, StationInfoModel
from .serializers import StationForecastRealDataSerializer, StationForecastRealDataComplexSerializer, \
    StationForecastRealDataRangeSerializer,StationForecastRealDataMixin
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

    # def get_relation_surge_range_value(self, station_code: str, forecast_dt_str: str, gp_id: int) -> {}:
    #     """
    #         由 station_code,forecast_dt_str,gp_id 获取 station surge 范围数据数组
    #     @param station_code:
    #     @param forecast_dt_str:
    #     @param ty_code:
    #     @param timestamp_str:
    #     @return:
    #     """
    #     forecast_dt: datetime = arrow.get(forecast_dt_str).datetime
    #     # query = StationForecastRealDataModel.objects.filter(gp_id=gp_id)
    #     # TODO:[*] 21-04-27 最后发现此种方式可行
    #     # select 就相当于是 sql 中的 SELECT 语句
    #     # tables 相当于 sql 中的 FROM
    #     # where 相当于 sql 中的 WHERE
    #     query = StationForecastRealDataModel.objects.filter(station_code=station_code, forecast_dt=forecast_dt,
    #                                                         gp_id=gp_id).extra(
    #         select={'station_code': 'station_forecast_realdata.station_code', 'lat': 'station_info.lat',
    #                 'lon': 'station_info.lon', 'name': 'station_info.name', 'surge': 'station_forecast_realdata.surge'},
    #         tables=['station_forecast_realdata', 'station_info'],
    #         where=['station_forecast_realdata.station_code=station_info.code'])
    #     # AttributeError: 'QuerySet' object has no attribute 'arregate'
    #     query = query.aggregate(Max('surge'), Min('surge'))
    #     return query

    def get_relation_surge_range_value(self, station_code: str, forecast_dt_str: str, ty_code: str,
                                       timestamp_str: str) -> {}:
        """
            由 station_code,forecast_dt_str,ty_code,timestamp_str 获取 station surge 范围数据数组
        @param station_code:
        @param forecast_dt_str:
        @param ty_code:
        @param timestamp_str:
        @return:
        """
        forecast_dt: datetime = arrow.get(forecast_dt_str).datetime
        # query = StationForecastRealDataModel.objects.filter(gp_id=gp_id)
        # TODO:[*] 21-04-27 最后发现此种方式可行
        # select 就相当于是 sql 中的 SELECT 语句
        # tables 相当于 sql 中的 FROM
        # where 相当于 sql 中的 WHERE
        query = StationForecastRealDataModel.objects.filter(station_code=station_code, forecast_dt=forecast_dt,
                                                            ty_code=ty_code, timestamp=timestamp_str).extra(
            select={'station_code': 'station_forecast_realdata.station_code', 'lat': 'station_info.lat',
                    'lon': 'station_info.lon', 'name': 'station_info.name', 'surge': 'station_forecast_realdata.surge'},
            tables=['station_forecast_realdata', 'station_info'],
            where=['station_forecast_realdata.station_code=station_info.code'])
        # AttributeError: 'QuerySet' object has no attribute 'arregate'
        query = query.aggregate(Max('surge'), Min('surge'))
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
                    'lon': 'station_info.lon', 'name': 'station_info.name', 'surge': 'station_forecast_realdata.surge'},
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


class StationSurgeRangeValueListView(StationListBaseView):
    """
        根据 forecast 与 ts 获取
        tb:station_forecast_realdata 与 tb:station_info
        获取预报范围值 和 当前中心路径的实际值
    """

    def get(self, request: Request) -> Response:
        """
            - 21-05-14 修改传入的参数由 ty_code | timestamp_str => gp_id
        @param request:
        @return:
        """
        is_paged = bool(int(request.GET.get('is_paged', '0')))
        ty_code: str = request.GET.get('ty_code', None)
        forecast_dt_str: datetime = request.GET.get('forecast_dt')
        timestamp_str: str = request.GET.get('timestamp', None)
        gp_id: int = int(request.GET.get('gp_id')) if request.GET.get('gp_id', None) is not None else DEFAULT_NULL_KEY
        page_index = request.GET.get('page_index', str(DEFAULT_PAGE_INDEX))
        page_count = DEFAULT_PAGE_COUNT
        query: List[StationForecastRealDataModel] = []
        stations: List[StationInfoModel] = self.get_all_station()
        stations_codes: List[int] = [temp.code for temp in stations]
        station_realdata_list: List[{}] = []
        station_finial_list: List[{}] = []
        # 方式2: 使用extra 的方式使用伪sql 代码实现 跨表拼接查询
        for temp_code in stations_codes:
            res = self.get_relation_surge_range_value(station_code=temp_code, forecast_dt_str=forecast_dt_str,
                                                      ty_code=ty_code, timestamp_str=timestamp_str)
            res['station_code'] = temp_code
            station_realdata_list.append(res)
            # 测试一下关联查询
            # res = query.union(stations)
            # if is_paged:
            #     paginator = Paginator(query, page_count)
            #     contacts = paginator.get_page(page_index)
        # TODO:[-] 21-05-14 此处还需要调用一下 self.get_relation_station
        res_station: List[StationForecastRealDataModel] = self.get_relation_station(gp_id=gp_id,
                                                                                    forecast_dt_str=forecast_dt_str)
        for temp_station in res_station:
            for temp_station_range in station_realdata_list:
                if temp_station.station_code == temp_station_range.get('station_code'):
                    temp_station.surge_max = temp_station_range.get('surge__max')
                    temp_station.surge_min = temp_station_range.get('surge__min')
                    station_finial_list.append(temp_station)

        try:

            self.json_data = StationForecastRealDataMixin(station_finial_list,
                                                                    many=True).data
            self._status = 200

        except Exception as ex:
            self.json = ex.args

        return Response(self.json_data, status=self._status)
