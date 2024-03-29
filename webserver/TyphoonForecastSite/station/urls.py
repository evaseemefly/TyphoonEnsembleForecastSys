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
    StationCenterMaxListView, StationAllPathMaxListView, StationSurgeSplitTab, StationBaseLevelDiffView, \
    StationD85DiffView, StationSurgeGroupRealListView, StationStaticsListView, StationListByGroupView, \
    StationTideDailyView, StationAstronomicTideListView, FamilyStationListView, DistStationAstronomicTideListView, \
    DistStationAlertView

app_name = '[station]'

urlpatterns = [
    # 根据查询条件获取 typhoonDetailModel 的列表
    url(r'^station/list/pid$', StationListByGroupView.as_view()),
    url(r'^station/tree/pid$', FamilyStationListView.as_view()),
    url(r'^station/list$', StationListView.as_view()),
    url(r'^tide/list$', StationTideDailyView.as_view()),
    url(r'^station/all/list$', StationStaticsListView.as_view()),  # + 22-07-21 获取全部的海洋站
    url(r'^station/center/max/list$', StationCenterMaxListView.as_view()),
    url(r'^station/allpath/max/list$', StationAllPathMaxListView.as_view()),
    url(r'^station/list/area$', StationAreaListView.as_view()),
    url(r'^station/realdata/range/list$', StationSurgeRangeValueListView.as_view()),
    url(r'^station/reallist/list$', StationSurgeRealListRangeValueView.as_view()),
    # - 22-07-04 加载潮位站 全部集合路径的 历史曲线及范围曲线
    url(r'^station/group/reallist/list$', StationSurgeGroupRealListView.as_view()),
    url(r'^station/astronomictide/range/list$', StationAstronomicTideRealDataListView.as_view()),
    url(r'^station/astronomictide/list$', StationAstronomicTideListView.as_view()),
    url(r'^station/dist/astronomictide/list$', DistStationAstronomicTideListView.as_view()),
    url(r'^station/alert$', StationAlertView.as_view()),
    # + 23-08-18 加载全部站点的警戒潮位集合
    url(r'^station/dist/alert$', DistStationAlertView.as_view()),
    url(r'^station/baseLevelDiff$', StationBaseLevelDiffView.as_view()),
    url(r'^station/d85$', StationD85DiffView.as_view()),
    url(r'^station/realdata/quarter/list$', StationSurgeRealDataQuarterListView.as_view()),

    url(r'^station/test$', StationSurgeSplitTab.as_view()),

]
