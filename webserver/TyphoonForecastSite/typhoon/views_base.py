#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/17 4:30 下午
# @Author  : evaseemefly
# @GithubSit: https://github.com/evaseemefly
# @Site    : 
# @File    : views_base.py
# @Software: PyCharm
from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework.request import Request
from django.db.models import Max, Min

from .models import TyphoonForecastDetailModel, TyphoonGroupPathModel, TyphoonForecastRealDataModel
from common.view_base import BaseView


class TypGroupBaseView(BaseView):
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
