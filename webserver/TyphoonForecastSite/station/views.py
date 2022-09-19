from django.shortcuts import render
import pathlib
from datetime import datetime
from os import path
from typing import List

import arrow
from django.shortcuts import render
from django.core.serializers import serialize
from django.db import connections, connection
from django.db import connection
from django.db.models import Max, Min
from django.db.models import QuerySet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)
from typing import List
# --
# 本项目的
# mid model
from .mid_models import StationTreeMidModel
# model
from .models import StationForecastRealDataModel, StationInfoModel, StationAstronomicTideRealDataModel, \
    StationAlertTideModel, StationStatisticsModel, StationForecastRealDataSharedMdoel, TideDataModel
from typhoon.models import TyphoonGroupPathModel
# 序列化器
from .serializers import StationForecastRealDataSerializer, StationForecastRealDataComplexSerializer, \
    StationForecastRealDataRangeSerializer, StationForecastRealDataMixin, StationForecastRealDataRangeComplexSerializer, \
    StationAstronomicTideRealDataSerializer, StationAlertSerializer, StationStatisticsSerializer, \
    StationForecastRealDataByGroupSerializer, StationInfoSerializer, TideDailyDataSerializer, StationTreeDataSerializer
# 公共的
from TyphoonForecastSite.settings import MY_PAGINATOR
from util.const import DEFAULT_NULL_KEY, UNLESS_TY_CODE, DEFAULT_CODE, DEFAULT_TIMTSTAMP_STR, \
    STATION_SURGE_REALDATA_TAB_BASE_NAME, DEFAULT_STATION_NAME
from common.view_base import BaseView
from typhoon.views_base import TyGroupBaseView
# 自定义装饰器
from util.customer_wrapt import get_time
from util.common import convert_str_2_utc_dt
from util.enum import AlertLevelEnum

DEFAULT_PAGE_INDEX = MY_PAGINATOR.get('PAGE_INDEX')
DEFAULT_PAGE_COUNT = MY_PAGINATOR.get('PAGE_COUNT')


class StationListBaseView(TyGroupBaseView):
    def get_dist_station_code(self, ty_code: str, timestamp_str: str) -> List[dict]:
        """
            + 获取 对应海洋站的code list
        @param ty_code:
        @param timestamp_str:
        @return:
        """
        stationSurgeRealDataDao = StationForecastRealDataSharedMdoel.get_sharding_model(ty_code=ty_code)
        dist_station_code: List[str] = stationSurgeRealDataDao.objects.filter(ty_code=ty_code,
                                                                              timestamp=timestamp_str).values(
            'station_code').distinct()
        return dist_station_code

    def get_all_station(self) -> List[StationInfoModel]:
        """
            获取全部的 非 is_del + is_abs 的station
        @return:
        """
        query: List[StationInfoModel] = StationInfoModel.objects.filter(is_abs=False, is_del=False, is_in_use=True)
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
            - 22-05-25 修改此处不使用 orm 的聚合函数实现，由于外侧需要循环，且为动态生产dao层，直接写入sql实现
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
        # base_filter = StationForecastRealDataModel.objects.filter(station_code=station_code, forecast_dt=forecast_dt,
        #                                                           ty_code=ty_code, timestamp=timestamp_str)
        stationSurgeRealDataDao = StationForecastRealDataSharedMdoel.get_sharding_model(ty_code=ty_code)
        tab_name: str = f'{StationForecastRealDataSharedMdoel.SHARED_TABLE_BASE_NAME}_{ty_code}'
        query = stationSurgeRealDataDao.objects.filter(station_code=station_code, forecast_dt=forecast_dt,
                                                       ty_code=ty_code, timestamp=timestamp_str).extra(
            select={'station_code': f'{tab_name}.station_code', 'lat': 'station_info.lat',
                    'lon': 'station_info.lon', 'name': 'station_info.name', 'surge': f'{tab_name}.surge'},
            tables=[f'{tab_name}', 'station_info'],
            where=[f'{tab_name}.station_code=station_info.code'])
        # AttributeError: 'QuerySet' object has no attribute 'arregate'
        query = query.aggregate(Max('surge'), Min('surge'))
        return query

    def get_all_path_surge_realdata_range_bygroup(self, forecast_dt_str: str, ty_code: str,
                                                  timestamp_str: str) -> tuple:
        """
            - 22-05-26 获取对应案例指定预报时刻的全路径不同潮位站的潮位范围
        @param forecast_dt_str:
        @param ty_code:
        @param timestamp_str:
        @return:{max,min,station_code}
        """
        forecast_dt: datetime = arrow.get(forecast_dt_str).datetime
        tab_name: str = f'{STATION_SURGE_REALDATA_TAB_BASE_NAME}_{ty_code}'
        forecast_dt_str: str = arrow.get()
        sql_str: str = f"""SELECT max(surge) as max,min(surge) as min,station_code as station_code,name,lat,lon,ty_code,forecast_dt,timestamp,forecast_index
                FROM (SELECT ({tab_name}.station_code) AS `station_code`,
                       (station_info.lat) AS `lat`, (station_info.lon) AS `lon`,
                       (station_info.name) AS `name`,
                       ({tab_name}.surge) AS `surge`,
                       `{tab_name}`.`id`,
                       `{tab_name}`.`is_del`,
                       `{tab_name}`.`gmt_created`,
                       `{tab_name}`.`gmt_modified`,
                       `{tab_name}`.`ty_code`,
                       `{tab_name}`.`gp_id`,
                       `{tab_name}`.`forecast_dt`,
                       `{tab_name}`.`forecast_index`,
                       `{tab_name}`.`timestamp`
                FROM `{tab_name}` , `station_info`
                WHERE (`{tab_name}`.`forecast_dt` = '{forecast_dt}' 
                AND `{tab_name}`.`ty_code` = {ty_code} AND `{tab_name}`.`timestamp` = '{timestamp_str}' AND (`{tab_name}`.`station_code`=station_info.code)) ) as res
        group by res.station_code"""
        with connection.cursor() as c:
            c.execute(sql_str)
            res = c.fetchall()
        return res

    def get_center_path_surge_realdata_range_bygroup(self, forecast_dt_str: str, ty_code: str,
                                                     timestamp_str: str, gp_id: int) -> tuple:
        """
            + 22-05-26 获取对应案例指定预报时刻的中间路径(gp_id)不同潮位站的潮位范围
        @param forecast_dt_str: 指定预报时刻(str)
        @param ty_code: 对应台风编号
        @param timestamp_str: 案例时间戳
        @param gp_id: 中间路径的 group path id
        @return:
        """
        forecast_dt: datetime = arrow.get(forecast_dt_str).datetime
        tab_name: str = f'{STATION_SURGE_REALDATA_TAB_BASE_NAME}_{ty_code}'
        forecast_dt_str: str = arrow.get()
        sql_str: str = f"""SELECT 
         ({tab_name}.surge) AS `surge`,
         ({tab_name}.station_code) AS `station_code`,(station_info.name) AS `name`,(station_info.lat) AS `lat`, (station_info.lon) AS `lon`,`{tab_name}`.`ty_code`,`{tab_name}`.`forecast_dt`,`{tab_name}`.`timestamp`,(station_info.base_level_diff) AS 'base_level_diff'  FROM `{tab_name}` , `station_info`
                       WHERE (`{tab_name}`.`forecast_dt` = '{forecast_dt}' AND `station_info`.`is_in_use`=TRUE
                       AND `{tab_name}`.`ty_code` = {ty_code} AND `{tab_name}`.`timestamp` = '{timestamp_str}'  AND `{tab_name}`.`gp_id` = '{gp_id}' AND (`{tab_name}`.`station_code`=station_info.code)) """
        with connection.cursor() as c:
            c.execute(sql_str)
            res = c.fetchall()
        return res

    def get_station_surge_max_value(self, station_code: str, gp_id: int, ty_code: str, dao):
        # TODO[*] 22-05-24 动态获取表此种方式速度很慢
        tab_name: str = f'{STATION_SURGE_REALDATA_TAB_BASE_NAME}_{ty_code}'

        # query = dao.objects.filter(station_code=station_code, gp_id=gp_id).extra(
        #     select={'station_code': f'{tab_name}.station_code', 'lat': 'station_info.lat',
        #             'lon': 'station_info.lon', 'name': 'station_info.name', 'surge': f'{tab_name}.surge'},
        #     tables=[f'{tab_name}', 'station_info'],
        #     where=[f'{tab_name}.station_code=station_info.code'])
        # query = query.aggregate(Max('surge'), Min('surge'))
        # ---
        # 方式2 : 不成功
        # query = dao.objects.raw(f"""SELECT max(surge) as max,min(surge) as min
        # FROM (SELECT ({tab_name}.station_code) AS `station_code`,
        #        (station_info.lat) AS `lat`, (station_info.lon) AS `lon`,
        #        (station_info.name) AS `name`,
        #        ({tab_name}.surge) AS `surge`,
        #        `{tab_name}`.`id`,
        #        `{tab_name}`.`is_del`,
        #        `{tab_name}`.`gmt_created`,
        #        `{tab_name}`.`gmt_modified`,
        #        `{tab_name}`.`ty_code`,
        #        `{tab_name}`.`gp_id`,
        #        `{tab_name}`.`forecast_dt`,
        #        `{tab_name}`.`forecast_index`,
        #        `{tab_name}`.`timestamp`
        # FROM `{tab_name}` , `station_info`
        # WHERE (`{tab_name}`.`gp_id` = {gp_id} AND `{tab_name}`.station_code = '{station_code}'
        #            AND ({tab_name}.station_code=station_info.code)) ) as res""",
        #                         translations={'max': 'max', 'min': 'min'})

        # 方式3:
        sql_str: str = f"""SELECT max(surge) as max,min(surge) as min
        FROM (SELECT ({tab_name}.station_code) AS `station_code`,
               (station_info.lat) AS `lat`, (station_info.lon) AS `lon`,
               (station_info.name) AS `name`,
               ({tab_name}.surge) AS `surge`,
               `{tab_name}`.`id`,
               `{tab_name}`.`is_del`,
               `{tab_name}`.`gmt_created`,
               `{tab_name}`.`gmt_modified`,
               `{tab_name}`.`ty_code`,
               `{tab_name}`.`gp_id`,
               `{tab_name}`.`forecast_dt`,
               `{tab_name}`.`forecast_index`,
               `{tab_name}`.`timestamp`
        FROM `{tab_name}` , `station_info`
        WHERE (`{tab_name}`.`gp_id` = {gp_id} AND `{tab_name}`.station_code = '{station_code}'
                   AND ({tab_name}.station_code=station_info.code)) ) as res"""
        with connection.cursor() as c:
            c.execute(sql_str)
            res = c.fetchall()
        return res

    def get_center_path_dist_station_surge_max_min_bygroup(self, gp_id: int, ty_code: str, dao) -> tuple:
        """
            - 22-05-25 获取中心路径对应的不同站点的极值(通过 group by 的方式聚合)——全过程
        @param gp_id:
        @param ty_code:
        @param dao:
        @return:(max,min,station_code)
        """

        tab_name: str = f'{STATION_SURGE_REALDATA_TAB_BASE_NAME}_{ty_code}'
        sql_str: str = f"""SELECT max(surge) as max,min(surge) as min,station_code as station_code
        FROM (SELECT ({tab_name}.station_code) AS `station_code`,
               (station_info.lat) AS `lat`, (station_info.lon) AS `lon`,
               (station_info.name) AS `name`,
               ({tab_name}.surge) AS `surge`,
               `{tab_name}`.`id`,
               `{tab_name}`.`is_del`,
               `{tab_name}`.`gmt_created`,
               `{tab_name}`.`gmt_modified`,
               `{tab_name}`.`ty_code`,
               `{tab_name}`.`gp_id`,
               `{tab_name}`.`forecast_dt`,
               `{tab_name}`.`forecast_index`,
               `{tab_name}`.`timestamp`
        FROM `{tab_name}` , `station_info`
        WHERE (`{tab_name}`.`gp_id` = {gp_id} AND `station_info`.`is_in_use`=TRUE
                   AND ({tab_name}.station_code=station_info.code)) ) as res
group by res.station_code"""
        with connection.cursor() as c:
            c.execute(sql_str)
            res = c.fetchall()
        return res

    def get_all_path_dist_station_surge_max_min_bygroup(self, timestamp: str, ty_code: str, dao) -> tuple:
        """
            - 22-05-25 获取该过程(timestamp——该时间戳只为创建case时生成的时间戳与预报时间无关)全路径的不同站点的极值(通过 group by 的方式聚合)
            此计算较为耗时(8-9s)
        @param timestamp: 创建case的时间戳(用来区分不同的案例)
        @param ty_code: 台风编号
        @param dao:
        @return:(max,min,station_code)
        """
        tab_name: str = f'{STATION_SURGE_REALDATA_TAB_BASE_NAME}_{ty_code}'
        sql_str: str = f"""SELECT max(surge) as max,min(surge) as min,station_code as station_code
                FROM (SELECT ({tab_name}.station_code) AS `station_code`,
                       (station_info.lat) AS `lat`, (station_info.lon) AS `lon`,
                       (station_info.name) AS `name`,
                       ({tab_name}.surge) AS `surge`,
                       `{tab_name}`.`id`,
                       `{tab_name}`.`is_del`,
                       `{tab_name}`.`gmt_created`,
                       `{tab_name}`.`gmt_modified`,
                       `{tab_name}`.`ty_code`,
                       `{tab_name}`.`gp_id`,
                       `{tab_name}`.`forecast_dt`,
                       `{tab_name}`.`forecast_index`,
                       `{tab_name}`.`timestamp`
                FROM `{tab_name}` , `station_info`
                 WHERE ( {tab_name}.timestamp= {timestamp}  AND ({tab_name}.station_code=station_info.code)) ) as res
        group by res.station_code"""
        with connection.cursor() as c:
            c.execute(sql_str)
            res = c.fetchall()
        return res

    # @get_time
    def get_station_all_path_surge_max(self, station_code: str, timestamp_str: str, ty_code: str, **kwargs):
        """
            + 22-02-15
            获取指定 ty_code 与 timestamp_str 对应的 潮位站 的全路径中的极值(max,min)
        """
        stationSurgeRealDataDao = StationForecastRealDataSharedMdoel.get_sharding_model(ty_code=ty_code)
        query = stationSurgeRealDataDao.objects.filter(station_code=station_code, timestamp=timestamp_str,
                                                       ty_code=ty_code).values('surge')
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
            dao = StationForecastRealDataSharedMdoel.get_sharding_model(ty_code=ty_code)
            qs_real_data = dao.objects.filter(station_code=station_code, ty_code=ty_code,
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
        dao = StationForecastRealDataSharedMdoel.get_sharding_model(ty_code=ty_code)
        qs_dist_forecast_dt: QuerySet = dao.objects.filter(station_code=station_code,
                                                           ty_code=ty_code,
                                                           timestamp=timestamp).values(
            'forecast_dt').distinct()
        list_dist_forecast_dt = [temp.get('forecast_dt') for temp in qs_dist_forecast_dt]

        # 根据 forecast_dt dist list -> tb:station_forecast_realdata
        dao = StationForecastRealDataSharedMdoel.get_sharding_model(ty_code=ty_code)
        res: QuerySet = dao.objects.filter(station_code=station_code, ty_code=ty_code,
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


class StationListByGroupView(StationListBaseView):
    def get(self, request: Request) -> Response:
        pid = int(request.GET.get('pid', str(DEFAULT_NULL_KEY)))
        fathers = StationInfoModel.objects.filter(pid=pid, is_in_use=True)
        res = StationInfoSerializer(fathers, many=True).data
        self.json_data = res
        self._status = 200
        return Response(self.json_data, status=self._status)


class FamilyStationListView(StationListBaseView):
    """
        + 22-09-08 根据传入的 pid 获取pid为传入pid的所有 father 及嵌套 children 数组
    """

    def get(self, request: Request) -> Response:
        pid = int(request.GET.get('pid', str(DEFAULT_NULL_KEY)))
        fathers = StationInfoModel.objects.filter(pid=pid, is_in_use=True)
        station_list: List[StationTreeMidModel] = []
        try:
            for father in fathers:
                father_tree_mid: StationTreeMidModel = StationTreeMidModel(father.id, father.name, father.code,
                                                                           is_abs=father.is_abs, sort=father.sort,
                                                                           children=[])
                children = StationInfoModel.objects.filter(pid=father.id, is_in_use=True, is_del=False)
                children_tree_mid: List[StationTreeMidModel] = []
                for child in children:
                    grandson = StationInfoModel.objects.filter(pid=child.id)
                    child_tree_mid: StationTreeMidModel = StationTreeMidModel(child.id, child.name, child.code,
                                                                              is_abs=child.is_abs, sort=child.sort,
                                                                              children=[])
                    if grandson.count() > 0:
                        grandsons = []
                        for temp in grandson:
                            grandson_tree: StationTreeMidModel = StationTreeMidModel(temp.id, temp.name,
                                                                                     temp.code, temp.is_abs, temp.sort,
                                                                                     [])
                            grandsons.append(grandson_tree)
                        child_tree_mid.children = grandsons
                    children_tree_mid.append(child_tree_mid)
                if children.count() > 0:
                    father_tree_mid.children = children_tree_mid
                station_list.append(father_tree_mid)
            res = StationTreeDataSerializer(station_list, many=True).data
            self.json_data = res
            self._status = 200
        except Exception as ex:
            self.json_data = ex.args
            # self._status=500
        return Response(self.json_data, status=self._status)


class StationStaticsListView(StationListBaseView):
    """
        + 22-07-21 获取海洋站静态信息列表
    """

    def get(self, request: Request) -> Response:
        list_station = self.get_all_station()
        self.json_data = StationInfoSerializer(list_station, many=True).data
        self._status = 200
        return Response(self.json_data, status=self._status)


class StationCenterMaxListView(StationListBaseView):
    """
        + 22-02-11 获取台风中心路径 c bp=0 的所有潮位站的极值(max)
        TODO:[-] 22-05-24 此方法暂时不会被调用
    """

    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', DEFAULT_CODE)
        timestamp_str: str = request.GET.get('timestamp', DEFAULT_TIMTSTAMP_STR)
        station_realdata_list: List[{}] = []
        if ty_code != DEFAULT_CODE and timestamp_str != DEFAULT_TIMTSTAMP_STR:
            center_path: TyphoonGroupPathModel = TyphoonGroupPathModel.objects.filter(ty_code=ty_code,
                                                                                      timestamp=timestamp_str,
                                                                                      ty_path_type='c', bp=0).first()
            gp_id = center_path.id
            dist_station_codes: List[dict] = self.get_dist_station_code(ty_code, timestamp_str)
            dao = StationForecastRealDataSharedMdoel.get_sharding_model(ty_code=ty_code)
            for station_code_temp in dist_station_codes:
                res = self.get_station_surge_max_value(station_code_temp.get('station_code'), gp_id, ty_code, dao)
                station_temp = StationInfoModel.objects.filter(code=station_code_temp.get('station_code')).first()
                res['station_code'] = station_code_temp.get('station_code')
                res['surge_max'] = res['surge__max']
                res['surge_min'] = res['surge__min']
                res['surge'] = res['surge__max']
                res['name'] = station_temp.name
                res['lat'] = station_temp.lat
                res['lon'] = station_temp.lon
                res['ty_code'] = ty_code
                station_realdata_list.append(res)
        try:

            self.json_data = StationForecastRealDataMixin(station_realdata_list,
                                                          many=True).data
            self._status = 200

        except Exception as ex:
            self.json = ex.args
        return Response(data=self.json_data, status=self._status)


class StationAllPathMaxListView(StationListBaseView):
    """
        + 22-02-14 海洋站极值风暴增水显示视图
        - 22-05-24 此处尝试将 surge_max 与 surge_min 修改为全部路径，但较为耗时(8-9s)固只采用中间路径的极值范围(全过程)
        response :{
                    "ty_code": "2042",
                    "station_code": "BAO",
                    "surge": 0.0,           - 中间路径的最大值
                    "name": "博鳌",
                    "lat": 19.2,
                    "lon": 110.6,
                    "surge_max": 1.26       - 中间路径的极大值(全过程)
                    "surge_min"             - 中间路径的极小值(全过程)
                },
    """

    @get_time
    def get(self, request: Request) -> Response:
        """
            step:
                1- 找到中间路径 gp_id
                2- 使用聚合函数获取中间路径的该案例的全过程 的极值范围
        """
        ty_code: str = request.GET.get('ty_code', DEFAULT_CODE)
        timestamp_str: str = request.GET.get('timestamp', DEFAULT_TIMTSTAMP_STR)
        station_realdata_list: List[{}] = []

        def filter_station(station_temp: {}, station_code: str) -> {}:
            if station_temp.station_code == station_code:
                return station_temp

        if ty_code != DEFAULT_CODE and timestamp_str != DEFAULT_TIMTSTAMP_STR:
            # dist_station_codes: List[dict] = list(self.get_dist_station_code(ty_code, timestamp_str))
            center_path: TyphoonGroupPathModel = TyphoonGroupPathModel.objects.filter(ty_code=ty_code,
                                                                                      timestamp=timestamp_str,
                                                                                      ty_path_type='c', bp=0).first()
            gp_id = center_path.id
            # station_codes: List[str] = [station_code_temp.get('station_code') for station_code_temp in
            #                             dist_station_codes]
            # station_codes_str: str = ''
            # for station_code in station_codes:
            #     station_codes_str = station_codes_str + f'\'{station_code}\','
            # station_codes_str = station_codes_str[:-1]
            # 获取指定 station_code 的对应的所有路径的极值
            """
                SELECT station_code,MAX(surge)
                FROM station_forecast_realdata
                WHERE (station_forecast_realdata.station_code in ('PTN','FQH','SCH','FHW') AND station_forecast_realdata.timestamp = 1644027304 AND
                       station_forecast_realdata.ty_code = 2042)
                GROUP BY station_forecast_realdata.station_code
            """

            # 方式2: 也较为耗时
            # cursor = connection.cursor()  # cursor = connections['default'].cursor()
            # cursor.execute(sql_str)
            # surge_max_res = cursor.fetchall()
            # # res = StationForecastRealDataModel.objects.raw(sql_str)
            # # eg: ('BAO', 1.26)  0:station_code , 1:max
            # for temp in surge_max_res:
            #     res = {}
            #     station_code_temp: str = temp[0]
            #     res['station_code'] = station_code_temp
            #     res['surge_max'] = temp[1]
            #     res_center_path = self.get_station_surge_max_value(station_code_temp, gp_id)
            #     station_temp = StationInfoModel.objects.filter(code=station_code_temp).first()
            #     res['surge'] = res_center_path['surge__max']
            #     res['name'] = station_temp.name
            #     res['lat'] = station_temp.lat
            #     res['lon'] = station_temp.lon
            #     res['ty_code'] = ty_code
            #     station_realdata_list.append(res)
            # 方式2:使用如下方式会造成查询变慢

            stationSurgeRealDataDao = StationForecastRealDataSharedMdoel.get_sharding_model(ty_code=ty_code)
            # [-] 22-05-25 不再使用之前根据不同的 station_code 进行循环的方式，直接修改为聚合的方式求max与min
            res_tuple = self.get_center_path_dist_station_surge_max_min_bygroup(gp_id, ty_code, stationSurgeRealDataDao)
            for temp in res_tuple:
                station_code = temp[2]
                surge_max = temp[0]
                surge_min = temp[1]
                station_temp = StationInfoModel.objects.filter(code=station_code).first()
                res = {}
                res['station_code'] = station_code
                res['surge_max'] = surge_max
                res['surge_min'] = surge_min
                res['surge'] = surge_max
                res['name'] = station_temp.name
                res['lat'] = station_temp.lat
                res['lon'] = station_temp.lon
                res['ty_code'] = ty_code
                station_realdata_list.append(res)
        try:

            self.json_data = StationForecastRealDataMixin(station_realdata_list,
                                                          many=True).data
            self._status = 200

        except Exception as ex:
            self.json = ex.args
        return Response(data=self.json_data, status=self._status)


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
            dao = StationForecastRealDataSharedMdoel.get_sharding_model(ty_code=ty_code)
            dist_station_code: List[str] = dao.objects.filter(ty_code=ty_code,
                                                              timestamp=timestamp_str).values(
                'station_code').distinct()
            if len(dist_station_code) > 0:
                for station_code_dict_temp in dist_station_code:
                    station_temp: StationInfoModel = StationInfoModel.objects.filter(
                        code=station_code_dict_temp.get('station_code'), is_in_use=True).first()
                    if station_temp is not None:
                        list_station_info.append(station_temp)
                        list_station_real.append(
                            {'ty_code': ty_code, 'station_code': station_temp.code, 'surge': 0,
                             'name': station_temp.name,
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
        - 22-05-26 注意现在反悔的是全部路径中的极值，非中间路径
    """

    def get(self, request: Request) -> Response:
        """
            - 21-05-14 修改传入的参数由 ty_code | timestamp_str => gp_id
            - 获取该时刻的所有海洋站的当前预报时刻(forecast_dt,ty_code,timestamp_str)
              的中间路径(前台传入的gp_id)的潮位置及其余路径中的max与min
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
        # TODO:[-] 22-05-25 由于使用了分表，此处的dao层是动态生成的，循环起来效率较低，改为直接使用聚合sql执行并返回
        # 之前的方式: 修改为分表动态生成dao后循环查询效率下降较明显
        # for temp_code in stations_codes:
        #     res = self.get_relation_surge_range_value(station_code=temp_code, forecast_dt_str=forecast_dt_str,
        #                                               ty_code=ty_code, timestamp_str=timestamp_str)
        #     res['station_code'] = temp_code
        #     station_realdata_list.append(res)
        # 方式2:
        """
            eg: (0.0, 0.0, 'PTN', '平潭', 25.4667, 119.8333, '2107', datetime.datetime(2021, 7, 19, 6, 0), '1650352587')
                 max ,min, staiton_code,name,lat,lon,ty_code,forecast_dt,timestamp
                 0   , 1  , 2   ,   3,    4     ,     5    ,    6   ,   7                               ,       8
            ---
            22-06-09 
            取消了聚合，因为查询条件为中间路径(指定了gp_id)，只有一条结果
            ('PTN', 25.4667, 119.8333, '平潭', 2.71, 118868, '2107', 12774, datetime.datetime(2021, 7, 20, 7, 0), 19, '1654763175')
            ---
            {tab_name}.station_code) AS `station_code`,
                              (station_info.lat) AS `lat`, (station_info.lon) AS `lon`,
                              (station_info.name) AS `name`,
                              ({tab_name}.surge) AS `surge`,
                              `{tab_name}`.`id`,
                              `{tab_name}`.`ty_code`,
                              `{tab_name}`.`gp_id`,
                              `{tab_name}`.`forecast_dt`,
                              `{tab_name}`.`forecast_index`,
                              `{tab_name}`.`timestamp`
            ---
            最新的返回结果
            (0.13, 'PTN', '平潭', 25.4667, 119.8333, '2107', datetime.datetime(2021, 7, 20, 5, 0), '1654763175')
     max ,min, staiton_code,name,lat,   lon,        ty_code,forecast_dt,                    timestamp
     0   , 1  , 2   ,       3,    4     ,5    ,      6   ,                                  7     
        """
        res_tuple: tuple = self.get_center_path_surge_realdata_range_bygroup(forecast_dt_str=forecast_dt_str,
                                                                             ty_code=ty_code,
                                                                             timestamp_str=timestamp_str, gp_id=gp_id)
        for temp in res_tuple:
            temp_station = {}
            temp_station['station_code'] = temp[1]
            temp_station['ty_code'] = temp[5]
            temp_station['gp_id'] = gp_id
            temp_station['forecast_index'] = temp[7]
            temp_station['forecast_dt'] = temp[6]
            temp_station['surge'] = temp[0]
            temp_station['name'] = temp[2]
            temp_station['lat'] = temp[3]
            temp_station['lon'] = temp[4]
            temp_station['surge_max'] = temp[0]
            temp_station['surge_min'] = temp[0]
            temp_station['base_level_diff'] = temp[8]
            station_finial_list.append(temp_station)
        # ---
        # -----耗时查询结束-----
        # 测试一下关联查询
        # res = query.union(stations)
        # if is_paged:
        #     paginator = Paginator(query, page_count)
        #     contacts = paginator.get_page(page_index)
        # TODO:[-] 21-05-14 此处还需要调用一下 self.get_relation_station
        # res_station: List[StationForecastRealDataModel] = self.get_relation_station(gp_id=gp_id,
        #                                                                             forecast_dt_str=forecast_dt_str)
        # for temp_station in res_station:
        #     for temp_station_range in station_realdata_list:
        #         if temp_station.station_code == temp_station_range.get('station_code'):
        #             temp_station.surge_max = temp_station_range.get('surge__max')
        #             temp_station.surge_min = temp_station_range.get('surge__min')
        #             station_finial_list.append(temp_station)

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


class StationSurgeGroupRealListView(StationListBaseView):
    """
        + 22-07-04 加载潮位站 全部集合路径的 历史曲线及范围曲线
    """

    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', None)
        timestamp_str: str = request.GET.get('timestamp', None)
        station_code: str = request.GET.get('station_code', None)
        # 获取指定case 的集合
        dict_group_models = {}

        query = self.get_surge_list_groupby_gp(ty_code=ty_code, timestamp_str=timestamp_str,
                                               station_code=station_code)

        list_temp = []
        for temp in query:
            temp_surge = {}
            temp_dict = {'forecast_index': temp.forecast_index, 'surge': temp.surge}
            if temp.gp_id not in dict_group_models:
                dict_group_models[temp.gp_id] = {}
                dict_group_models[temp.gp_id]['list_realdata'] = []
                dict_group_models[temp.gp_id]['list_realdata'].append(temp_dict)
            elif temp.gp_id in dict_group_models:
                dict_group_models[temp.gp_id]['list_realdata'].append(temp_dict)
            # print(temp)
        # self.json_data = list_ids
        # {'gp_id': 14361,
        # 'list_realdata': [
        # <StationForecastRealDataModel: StationForecastRealDataModel object (1856853)>
        list_group_models = []
        for key, val in dict_group_models.items():
            list_group_models.append({'gp_id': key,
                                      'list_realdata': val['list_realdata']})
        # ERROR: The serializer field might be named incorrectly and not match any attribute or key on the `list` instance.
        # Original exception text was: 'list' object has no attribute 'ty_code'.
        res = StationForecastRealDataByGroupSerializer(list_group_models, many=True).data
        self._status = 200
        self.json_data = res
        return Response(self.json_data, status=self._status)

    def get_dist_group_ids(self, ty_code: str, timestamp_str: str) -> List[int]:
        """
            + 22-07-04 指定case 的不同 group_id 集合
        @param timestamp_str:
        @return:
        """
        list_ids: List[int] = []
        dao = StationForecastRealDataSharedMdoel.get_sharding_model(ty_code=ty_code)
        # 获取集合路径 id 集合
        list_ids = [temp.get('gp_id') for temp in
                    dao.objects.filter(ty_code=ty_code, timestamp=timestamp_str).values('gp_id').distinct()]
        return list_ids

    def get_surge_list_groupby_gp(self, ty_code: str, timestamp_str: str, station_code: str):
        """
            + 22-07-04 根据 gp_id 进行聚合 查找对应 case 的海洋站潮位数据
        @param ty_code:
        @param timestamp_str:
        @param station_code:
        @return:
        """
        dao = StationForecastRealDataSharedMdoel.get_sharding_model(ty_code=ty_code)
        db_table_name: str = StationForecastRealDataSharedMdoel.get_sharding_tb_name(ty_code=ty_code)
        # query_sql: str = f"""
        #                 select *
        #                 from {db_table_name}
        #                 where ty_code='{ty_code}' and station_code='{station_code}' and timestamp='{timestamp_str}'
        #                 group by gp_id
        # """
        query_sql: str = f"""
                                select gp_id,forecast_index,ANY_VALUE(surge) as surge,ANY_VALUE(ty_code) as ty_code,ANY_VALUE(id) as id
                                from {db_table_name}
                                where ty_code='{ty_code}' and station_code='{station_code}' and timestamp='{timestamp_str}'
                                group by gp_id,forecast_index
                """
        # cursor = connection.cursor()
        # cursor.execute(query_sql)
        # ret = cursor.fetchall()
        query = dao.objects.raw(query_sql, translations={'ty_code': 'ty_code',
                                                         'forecast_index': 'forecast_index',
                                                         'surge': 'surge', 'gp_id': 'gp_id'})
        return query


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


class StationAstronomicTideListView(StationListBaseView):
    '''
        + 22-08-05 根据 station_code | start_dt | end_dt 获取对应天文潮集合
    '''

    def get(self, request: Request) -> Response:
        station_code: str = request.GET.get('station_code', None) if request.GET.get('station_code',
                                                                                     None) is not None else DEFAULT_CODE
        start_dt_str: str = request.GET.get('start_dt')
        end_dt_str: str = request.GET.get('end_dt')
        start_dt: datetime = arrow.get(start_dt_str).datetime
        end_dt: datetime = arrow.get(end_dt_str).datetime
        query: QuerySet = StationAstronomicTideRealDataModel.objects.filter(station_code=station_code).filter(
            forecast_dt__lte=end_dt, forecast_dt__gte=start_dt)
        self.json_data = StationAstronomicTideRealDataSerializer(query, many=True).data
        self._status = 200
        return Response(self.json_data, status=self._status)


class StationBaseLevelDiffView(BaseView):
    def get(self, request: Request):
        station_code: str = request.GET.get('station_code', DEFAULT_CODE)
        diffObj: {} = {}
        diffObj['station_code'] = station_code
        if station_code != DEFAULT_CODE:
            station_res = StationInfoModel.objects.filter(code=station_code)
            if len(station_res) == 1:
                diffObj['surge_diff'] = station_res.first().base_level_diff
                self._status = 200
        self.json_data = diffObj
        return Response(self.json_data, status=self._status)


class StationD85DiffView(BaseView):
    def get(self, request: Request):
        station_code: str = request.GET.get('station_code', DEFAULT_CODE)
        diffObj: {} = {}
        diffObj['station_code'] = station_code
        if station_code != DEFAULT_CODE:
            station_res = StationInfoModel.objects.filter(code=station_code)
            if len(station_res) == 1:
                diffObj['d85_diff'] = station_res.first().d85
                self._status = 200
        self.json_data = diffObj
        return Response(self.json_data, status=self._status)


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


class StationSurgeSplitTab(BaseView):
    def get(self, request: Request):
        ty_code: str = '2017'
        dao = StationForecastRealDataSharedMdoel.get_sharding_model(ty_code=ty_code)
        query = dao.objects.filter(id=1)
        return Response('', status=200)


class StationTideDailyView(StationListBaseView):
    """
        + 22-07-31 当日高潮位视图
    """

    def get(self, request: Request) -> Response:
        """
            + 22-08-01 获取起止日期之间的指定潮位站集合的高潮值集合
        """
        # station_codes_str: str = request.GET.get('station_codes', '')
        # station_codes = station_codes_str.split(',')
        station_codes = request.GET.getlist('station_codes[]', [])
        # TODO:[-] 22-08-09 注意传入的时间为 utc 时间 00Z 不需要手动转换为 utc 时间，后台处理时统一使用utc时间
        start_dt_str: str = request.GET.get('forecast_start_dt')
        end_dt_str: str = request.GET.get('forecast_end_dt')
        '''
            stationName: '测试1',
			stationCode: 'CES1',
			id: 1,
			surgeList: [
				{ forecastDt: new Date(), surge: 215 },
				{ forecastDt: new Date(), surge: 108 },
			],
			blue: 120,
			yellow: 140,
			orgin: 160,
			red: 180,
        '''
        start_dt_utc: datetime = convert_str_2_utc_dt(start_dt_str, False)
        end_dt_utc: datetime = convert_str_2_utc_dt(end_dt_str, False)
        list_tide: List[dict] = []
        # step2: 根据提交的 station_codes 遍历，根据对应的 station_code以及起止时间获取高潮值
        for station_code in station_codes:
            tides = TideDataModel.objects.filter(station_code=station_code, forecast_dt__gte=start_dt_utc,
                                                 forecast_dt__lte=end_dt_utc)
            station_name = DEFAULT_STATION_NAME
            d85 = None
            base_level_diff = None
            if StationInfoModel.objects.filter(code=station_code).first() is not None:
                stationInfo = StationInfoModel.objects.filter(code=station_code).first()
                station_name = stationInfo.name
                d85 = stationInfo.d85
                base_level_diff = stationInfo.base_level_diff
            tide_dict = {}
            tide_dict['station_name'] = station_name
            tide_dict['station_code'] = station_code
            tide_dict['d85'] = d85
            tide_dict['base_level_diff'] = base_level_diff
            tide_dict['surge_list'] = []
            for tide in tides:
                tide_temp: {} = {}
                tide_temp['forecast_dt'] = tide.forecast_dt
                tide_temp['surge'] = tide.surge
                tide_dict['surge_list'].append(tide_temp)
                # 生成四色警戒潮位
                alert_levels = StationAlertTideModel.objects.filter(station_code=station_code)
                for level in alert_levels:
                    if level.alert == AlertLevelEnum.BLUE.value:
                        tide_dict['blue'] = level.tide
                    elif level.alert == AlertLevelEnum.YELLOW.value:
                        tide_dict['yellow'] = level.tide
                    elif level.alert == AlertLevelEnum.ORANGE.value:
                        tide_dict['orange'] = level.tide
                    elif level.alert == AlertLevelEnum.RED.value:
                        tide_dict['red'] = level.tide
            list_tide.append(tide_dict)

            pass
        json_data = TideDailyDataSerializer(list_tide, many=True).data
        self._status = 200
        self.json_data = json_data
        return Response(self.json_data, status=self._status)
