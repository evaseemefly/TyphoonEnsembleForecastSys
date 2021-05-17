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

from .models import TyphoonForecastDetailModel, TyphoonGroupPathModel, TyphoonForecastRealDataModel
from common.view_base import BaseView


class TypGroupBaseView(BaseView):
    def getCenterGroupPath(self, **kwargs) -> QuerySet:
        timestamp_str: str = kwargs.get('timestamp')
        ty_code: str = kwargs.get('ty_code')
        ty_id: int = kwargs.get('ty_id')
        query: QuerySet = TyphoonGroupPathModel.objects.filter(ty_code=ty_code, timestamp=timestamp_str)
        query = query.filter(ty_path_type='c', ty_path_marking=0, bp=0)
        # TODO:[-] 21-05-17 此处应加入 判断 query 的长度是否不为1，不为1则说明结果不止一个或没有，待抛出异常
        return query
