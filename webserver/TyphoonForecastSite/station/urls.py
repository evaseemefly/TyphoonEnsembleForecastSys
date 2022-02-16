#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/25 21:11
# @Author  : evaseemefly
# @Desc    :
# @Site    :
# @File    : urls.py
# @Software: PyCharm
from django.conf.urls import url, include

from rest_framework import routers

# 本项目
from .views import StationListView, StationSurgeRangeValueListView, StationSurgeRealListRangeValueView, \
    StationAstronomicTideRealDataListView, StationAlertView, StationSurgeRealDataQuarterListView, StationAreaListView, \
    StationCenterMaxListView, StationAllPathMaxListView

app_name = '[station]'

urlpatterns = [
    # 根据查询条件获取 typhoonDetailModel 的列表
    url(r'^station/list$', StationListView.as_view()),
    url(r'^station/center/max/list$', StationCenterMaxListView.as_view()),
    url(r'^station/allpath/max/list$', StationAllPathMaxListView.as_view()),
    url(r'^station/list/area$', StationAreaListView.as_view()),
    url(r'^station/realdata/range/list$', StationSurgeRangeValueListView.as_view()),
    url(r'^station/reallist/list$', StationSurgeRealListRangeValueView.as_view()),
    url(r'^station/astronomictide/range/list$', StationAstronomicTideRealDataListView.as_view()),
    url(r'^station/alert$', StationAlertView.as_view()),
    url(r'^station/realdata/quarter/list$', StationSurgeRealDataQuarterListView.as_view()),

]
