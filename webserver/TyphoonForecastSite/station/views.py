from django.shortcuts import render
import pathlib
from datetime import datetime
from os import path
from typing import List

import arrow
from django.shortcuts import render
from django.core.serializers import serialize
from django.db.models import Max, Min
from django.db.models import QuerySet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)

# --
# 本项目的
from .models import StationForecastRealDataModel, StationInfoModel, StationAstronomicTideRealDataModel, \
    StationAlertTideModel, StationStatisticsModel
from .serializers import StationForecastRealDataSerializer, StationForecastRealDataComplexSerializer, \
    StationForecastRealDataRangeSerializer, StationForecastRealDataMixin, StationForecastRealDataRangeComplexSerializer, \
    StationAstronomicTideRealDataSerializer, StationAlertSerializer, StationStatisticsSerializer
# 公共的
from TyphoonForecastSite.settings import MY_PAGINATOR
from util.const import DEFAULT_NULL_KEY, UNLESS_TY_CODE, DEFAULT_CODE, DEFAULT_TIMTSTAMP_STR
from common.view_base import BaseView
from typhoon.views_base import TyGroupBaseView
# 自定义装饰器
from util.customer_wrapt import get_time

DEFAULT_PAGE_INDEX = MY_PAGINATOR.get('PAGE_INDEX')
DEFAULT_PAGE_COUNT = MY_PAGINATOR.get('PAGE_COUNT')


class StationListBaseView(TyGroupBaseView):
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

    @get_time
    def get_surge_list(self, station_code: str, gp_id: int) -> List[StationForecastRealDataModel]:
        """
            + 21-05-26 根据 station_code 与 gp_id 该站点的时序数据
        @param station_code:
        @param gp_id:
        @return:
        """
        res: List[StationForecastRealDataModel] = StationForecastRealDataModel.objects.filter(station_code=station_code,
                                                                                              gp_id=gp_id).all()
        return res

    @get_time
    def get_surge_realdata_dist_dt(self, station_code: str, ty_code: str, timestamp: str):
        """
            + 21-05-26 根据 station_code | ty_code | timestamp
            -> 中间路径对应的 tb:station_forecast_realdata
        @param station_code:
        @param ty_code:
        @param timestamp:
        @return:
        """
        qs_group_path: QuerySet = self.getCenterGroupPath(ty_code=ty_code, timestamp=timestamp)
        qs_real_data: QuerySet = None
        if (len(qs_group_path)) > 0:
            gp_center = qs_group_path.first()
            # 查询 tb:station_forecast_realdata 的条件有 : station_code | ty_code | timestamp | 中间路径 gp_id
            qs_real_data = StationForecastRealDataModel.objects.filter(station_code=station_code, ty_code=ty_code,
                                                                       timestamp=timestamp,
                                                                       gp_id=gp_center.id).values('forecast_dt',
                                                                                                  'surge').order_by(
                'forecast_dt')
        return qs_real_data
        pass

    # def get_target_ty_forecast_daterange(self,ty_code:str,timestamp:str):

    @get_time
    def get_surge_all_group(self, station_code: str, ty_code: str, timestamp: str):
        """
            + 21-05-26 根据 station_code | ty_code | timestamp
            -> tb:station_forecast_realdata
            by dist forecast_dt
            并 逐一求 max 与 min
        @param station_code:
        @param ty_code:
        @param timestamp:
        @return:
        """
        # TODO:[-] 21-05-26 Unable to get repr for <class 'method'>
        # 获取指定条件的全部 forecast_dt 的 dist list
        qs_dist_forecast_dt: QuerySet = StationForecastRealDataModel.objects.filter(station_code=station_code,
                                                                                    ty_code=ty_code,
                                                                                    timestamp=timestamp).values(
            'forecast_dt').distinct()
        list_dist_forecast_dt = [temp.get('forecast_dt') for temp in qs_dist_forecast_dt]

        # 根据 forecast_dt dist list -> tb:station_forecast_realdata
        res: QuerySet = StationForecastRealDataModel.objects.filter(station_code=station_code, ty_code=ty_code,
                                                                    timestamp=timestamp).extra(
            where=['forecast_dt in %s'], params=[list_dist_forecast_dt])
        # eg:
        # <class 'dict'>: {'forecast_dt': datetime.datetime(2020, 9, 15, 17, 0, tzinfo=<UTC>), 'surge_max': 0.0}
        res: QuerySet = res.values('forecast_dt').annotate(surge_max=Max('surge'), surge_min=Min('surge')).order_by(
            'forecast_dt')
        return res


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


class StationAreaListView(StationListBaseView):
    """
        根据传入的台风编号获取指定区域的海洋站站位信息
    """

    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', UNLESS_TY_CODE)
        timestamp_str: str = request.GET.get('timestamp', DEFAULT_TIMTSTAMP_STR)
        list_station_info: List[StationInfoModel] = []
        list_station_real: List[StationForecastRealDataModel] = []
        if ty_code != UNLESS_TY_CODE:
            # 1- 获取指定台风的所有海洋站 code
            dist_station_code: List[str] = StationForecastRealDataModel.objects.filter(ty_code=ty_code,
                                                                                       timestamp=timestamp_str).values(
                'station_code').distinct()
            if len(dist_station_code) > 0:
                for station_code_dict_temp in dist_station_code:
                    station_temp: StationInfoModel = StationInfoModel.objects.filter(
                        code=station_code_dict_temp.get('station_code')).first()
                    list_station_info.append(station_temp)
                    list_station_real.append(
                        {'ty_code': ty_code, 'station_code': station_temp.code, 'surge': 0, 'name': station_temp.name,
                         'lat': station_temp.lat, 'lon': station_temp.lon, 'gp_id': 0, 'forecast_dt': None,
                         'forecast_index': 0, 'timestamp': None, 'surge_max': 0, 'surge_min': 0})
            try:

                self.json_data = StationForecastRealDataMixin(list_station_real,
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
        # TODO:[*] 22-01-26 注意此处的查询较为耗时
        for temp_code in stations_codes:
            res = self.get_relation_surge_range_value(station_code=temp_code, forecast_dt_str=forecast_dt_str,
                                                      ty_code=ty_code, timestamp_str=timestamp_str)
            res['station_code'] = temp_code
            station_realdata_list.append(res)
        # -----耗时查询结束-----
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


class StationSurgeRealListRangeValueView(StationListBaseView):
    """
        + 21-05-26 加载潮位站 指定过程的 历史曲线以及范围曲线
    """

    @get_time
    def get(self, request: Request) -> Response:
        """
            + 21-05-26 ty_code | timestamp -> gp_id
              gp_id | station_code 找到对应的 tb: station_forecast_realdata 的数据集
        @param request:
        @return:
        """
        list_res: List[{}] = []
        ty_code: str = request.GET.get('ty_code', None)
        forecast_dt_str: datetime = request.GET.get('forecast_dt')
        timestamp_str: str = request.GET.get('timestamp', None)

        gp_id: int = int(request.GET.get('gp_id')) if request.GET.get('gp_id', None) is not None else DEFAULT_NULL_KEY
        station_code: str = request.GET.get('station_code', None) if request.GET.get('station_code',
                                                                                     None) is not None else DEFAULT_CODE
        self.get_surge_list(station_code, gp_id)
        # 包含 forecast_dt + surge_max + surge_min
        qs_surge_range = list(self.get_surge_all_group(station_code, ty_code, timestamp_str))
        # 包含 forecast_dt + surge
        qs_surge_realdatalist = list(self.get_surge_realdata_dist_dt(station_code, ty_code, timestamp_str))
        # 将两者拼接
        for index in range(len(qs_surge_range)):
            temp_range = qs_surge_range[index]
            temp_realdata = qs_surge_realdatalist[index]
            # {'forecast_dt': datetime.datetime(2020, 9, 15, 9, 0, tzinfo=<UTC>), 'surge_max': 0.0, 'surge_min': 0.0, 'surge': 0.0}
            # list_res.append({**temp_range, **temp_realdata})
            list_res.append({'forecast_dt': temp_range['forecast_dt'], 'surge_max': temp_range['surge_max'],
                             'surge_min': temp_range['surge_min'], 'surge': temp_realdata['surge']})
            # list_res.append({})
        self._status = 200
        # 序列化
        self.json_data = StationForecastRealDataRangeComplexSerializer(list_res, many=True).data
        return Response(self.json_data, status=self._status)

    pass


class StationSurgeRealDataQuarterListView(StationListBaseView):
    """
        + 21-10-29 加入 对于 中位数 ,1/4,3/4 百分位数的统计
    """

    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', None)
        forecast_dt_str: datetime = request.GET.get('forecast_dt', None)
        timestamp_str: str = request.GET.get('timestamp', None)
        station_code: str = request.GET.get('station_code', DEFAULT_CODE)
        query: QuerySet = None
        if any([ty_code, timestamp_str]) is not None and station_code is not DEFAULT_CODE:
            try:
                if forecast_dt_str is None:
                    query = StationStatisticsModel.objects.filter(ty_code=ty_code, station_code=station_code,
                                                                  timestamp=timestamp_str)
                else:
                    query = StationStatisticsModel.objects.filter(ty_code=ty_code, station_code=station_code,
                                                                  timestamp=timestamp_str, forecast_dt=forecast_dt_str)
                self.json_data = StationStatisticsSerializer(query, many=True).data
                self._status = 200
            except Exception as ex:
                self.json_data = ex.args
        return Response(self.json_data, status=self._status)
        pass


class StationAstronomicTideRealDataListView(StationListBaseView):
    '''
        + 21-08-24 天文潮位
    '''

    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', None)
        timestamp_str: str = request.GET.get('timestamp', None)
        station_code: str = request.GET.get('station_code', None) if request.GET.get('station_code',
                                                                                     None) is not None else DEFAULT_CODE
        list_query = self.get_station_tide(ty_code, timestamp_str, station_code)
        self.json_data = StationAstronomicTideRealDataSerializer(list_query, many=True).data
        self._status = 200
        return Response(self.json_data, status=self._status)
        pass

    def get_station_tide(self, ty_code: str, timestamp: str, station_code: str) -> List[
        StationAstronomicTideRealDataModel]:
        """
            + 21-08-24
            根据 台风编号 | 时间戳 | 获取该台风的预报起止时间
            获取对应海洋站的天文潮
        """
        dt_range: List[datetime] = self.get_ty_dtrange(ty_code, timestamp)
        query: QuerySet = None
        if len(dt_range) > 0:
            query: QuerySet = StationAstronomicTideRealDataModel.objects.filter(station_code=station_code).filter(
                forecast_dt__lte=dt_range[1], forecast_dt__gte=dt_range[0])
        return query[:]


class StationAlertView(StationListBaseView):
    def get(self, request: Request):
        """
            根据 station_code 获取对应海洋站的四色警戒潮位值
        """
        station_code: str = request.GET.get('station_code', None) if request.GET.get('station_code',
                                                                                     None) is not None else DEFAULT_CODE
        query = StationAlertTideModel.objects.filter(station_code=station_code, is_del=False)
        self.json_data = StationAlertSerializer(query, many=True).data
        self._status = 200
        return Response(self.json_data, status=self._status)
