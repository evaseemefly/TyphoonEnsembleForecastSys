#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/15 15:29
# @Author  : evaseemefly
# @Desc    :
# @Site    :
# @File    : urls.py
# @Software: PyCharm
from django.conf.urls import url, include

from rest_framework import routers

# 本项目
from .views import TyDetailModelView, TyGroupPathView, TyRealDataView, TyComplexGroupRealDatasetView, TyDataRangeView, \
    TyGroupDateDistView, TyList

app_name = '[typhoon]'

urlpatterns = [
    # + 21-07-22 根据年份获取台风列表
    url(r'^ty/list$', TyList.as_view()),
    # 根据查询条件获取 typhoonDetailModel 的列表
    url(r'^tyDetailModel/list$', TyDetailModelView.as_view()),
    # 根据查询条件获取 typhoonGroupPath 的列表
    url(r'^tyGroupPath/list$', TyGroupPathView.as_view()),
    # 根据查询条件获取 typhoonRealDataset 的列表
    url(r'^tyRealDataset/list$', TyRealDataView.as_view()),
    url(r'^tyComplex/group/realdata/list$', TyComplexGroupRealDatasetView.as_view()),
    url(r'^tyGroupPath/datarage$', TyDataRangeView.as_view()),
    url(r'^tyGroupPath/dist/date$', TyGroupDateDistView.as_view()),
]
