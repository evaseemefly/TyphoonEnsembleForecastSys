#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/4 6:21 下午
# @Author  : evaseemefly
# @GithubSit: https://github.com/evaseemefly
# @Site    : 
# @File    : urls.py
# @Software: PyCharm

from django.conf.urls import url, include

from rest_framework import routers

# 本项目
from .views import GeoTiffView

app_name = '[geo]'

urlpatterns = [
    # 根据查询条件获取 typhoonDetailModel 的列表
    url(r'^geotiff/url$', GeoTiffView.as_view()),

]
