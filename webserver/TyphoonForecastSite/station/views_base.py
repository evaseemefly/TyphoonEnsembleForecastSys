#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/4 4:57 下午
# @Author  : evaseemefly
# @GithubSit: https://github.com/evaseemefly
# @Site    : 
# @File    : views_base.py
# @Software: PyCharm
from datetime import datetime
# ----
from django.db.models import QuerySet
# ————
from .models import StationInfoModel, StationForecastRealDataModel
from common.interface import ICheckExisted

class StationCommonView(ICheckExisted):
    def __init__(self, **kwargs):
        pass

    def check_existed(self, ty_code: str, timestamp: str, forecast_dt: datetime) -> bool:
        """
            + 21-05-28
            根据 传入的参数 判断是否存在指定的 潮位站数据

        @param ty_code:
        @param timestamp:
        @param forecast_dt:
        @return:
        """
        isExisted: bool = False
        query: QuerySet = StationForecastRealDataModel.objects.filter(ty_code=ty_code, timestamp=timestamp)
        # 再根据 forecastDt 获取对应的值
        query = query.filter(forecast_dt=forecast_dt)
        if len(query) > 0:
            isExisted = True
        return isExisted
