#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/17 4:30 下午
# @Author  : evaseemefly
# @GithubSit: https://github.com/evaseemefly
# @Site    : 
# @File    : views_base.py
# @Software: PyCharm
from datetime import datetime, timedelta
from abc import abstractmethod
# ---
from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework.request import Request
from django.db.models import Max, Min

from typing import List

import arrow
from arrow.arrow import Arrow

from .models import TyphoonForecastDetailModel, TyphoonGroupPathModel, TyphoonForecastRealDataModel
from common.view_base import BaseView
from common.interface import ICheckExisted
from util.common import inter


class TyGroupBaseView(BaseView):
    def getCenterGroupPath(self, **kwargs) -> QuerySet:
        timestamp_str: str = kwargs.get('timestamp')
        ty_code: str = kwargs.get('ty_code')
        ty_id: int = kwargs.get('ty_id')
        # ty_group: TyphoonGroupPathModel
        query: QuerySet = TyphoonGroupPathModel.objects.filter(ty_code=ty_code, timestamp=timestamp_str)
        query = query.filter(ty_path_type='c', ty_path_marking=0, bp=0)

        # TODO:[-] 21-05-17 此处应加入 判断 query 的长度是否不为1，不为1则说明结果不止一个或没有，待抛出异常
        # if len(query) > 0:
        #     ty_group = query.first()
        return query

    def getCenterPathDateRange(self, ty_group: TyphoonGroupPathModel) -> []:
        date_range: [] = []
        # 1- 根据传入的 ty_group -> ty_forecast_realdata
        gp_id: int = ty_group.id
        # 2- 根据 gp id 找到该 gp 对应的一系列 ty_forecast_realdata 并取最大值与最小值
        query: QuerySet = TyphoonForecastRealDataModel.objects.filter(gp_id=gp_id)
        if len(query) > 2:
            dict_date_range = query.aggregate(Max('forecast_dt'), Min('forecast_dt'))
        date_range = [val for val in dict_date_range.values()]
        return date_range

    def getDateDist(self, ty_group: TyphoonGroupPathModel) -> List[datetime]:
        """
            查询指定 ty_group 的预报时刻
        @param ty_group:
        @return:
        """
        gp_id: int = ty_group.id

        # query: QuerySet = TyphoonForecastRealDataModel.objects.filter(gp_id=gp_id).distinct('forecast_dt')
        query: QuerySet = TyphoonForecastRealDataModel.objects.filter(gp_id=gp_id).order_by().values('forecast_dt')
        # list_dist_dt: List[datetime] = [temp.datetime for temp in query.all()]
        # 注意若使用 mysql 数据库 则无法使用 .distinct('field_name') 只能使用 .distinct()
        # TODO:[*] 21-05-17 ERROR
        # raise NotSupportedError('DISTINCT ON fields is not supported by this database backend')
        list_dist_dt: List[datetime] = [temp.get('forecast_dt') for temp in query.all()]
        return list_dist_dt

    def getDefaultDateRange(self, **kwargs) -> []:
        """
            + 21-05-18 加载默认的时间范围
                       默认的时间范围是 [当前时间的整点时刻,+24hour]
        @param ty_group:
        @return:
        """
        # TODO:[-] 21-05-18 注意此处若直接使用 datetime.utcnow ，生成的 datetime 是不带时区的，返回的json 中格式为
        # "2021-05-18T12:00:00"
        # 而正常的是:"2020-09-15T17:00:00Z"
        now: Arrow = arrow.utcnow()
        start_time: datetime = arrow.Arrow(now.year, now.month, now.day, now.hour, 0).datetime
        end_time: datetime = start_time + timedelta(hours=24)
        return [start_time, end_time]


class TyGroupCommonView(ICheckExisted):
    # @staticmethod
    def check_existed(self, ty_code: str, timestamp: str, forecast_dt: datetime) -> bool:
        """
            + 21-05-28
            根据 传入的参数 判断是否存在指定的 台风路径信息
            目前只从 -> tb: ty_forecast_detailinfo 中查找 gmt_start < forecast_dt and gmt_end > forecast_dt
        @param ty_code:
        @param timestamp:
        @param forecast_dt:
        @return:
        """
        isExisted: bool = False
        query_ty_detail: QuerySet = TyphoonForecastDetailModel.objects.filter(code=ty_code, gmt_start__lte=forecast_dt,
                                                                              gmt_end__gte=forecast_dt)
        query_ty_grouppath: QuerySet = TyphoonGroupPathModel.objects.filter(ty_code=ty_code, timestamp=timestamp)
        if len(query_ty_grouppath) > 0 and len(query_ty_detail) > 0:
            list_detial_ids: List[int] = [temp.id for temp in query_ty_detail]
            list_grouppath_tyids: List[int] = [temp.ty_id for temp in query_ty_grouppath]
            if len(inter(list_detial_ids, list_grouppath_tyids)) > 0:
                isExisted = True
        return isExisted
