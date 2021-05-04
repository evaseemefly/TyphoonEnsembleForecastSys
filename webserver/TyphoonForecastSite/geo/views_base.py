#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/4 4:58 下午
# @Author  : evaseemefly
# @GithubSit: https://github.com/evaseemefly
# @Site    : 
# @File    : views_base.py
# @Software: PyCharm

from django.shortcuts import render
import pathlib
from datetime import datetime
from os import path
from typing import List

import arrow
from django.shortcuts import render
from django.core.serializers import serialize
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)

# 本项目中的
from common.view_base import BaseView
from util.const import DEFAULT_NULL_KEY
from .models import CoverageInfoModel, ForecastTifModel
from TyphoonForecastSite.settings import STORE_OPTIONS
from util.exception import NoneError


class RasterBaseView(BaseView):
    def get_coverage(self, id: int = DEFAULT_NULL_KEY, **kwargs) -> CoverageInfoModel:
        """
            获取 对应的 coverage
        @param id:
        @param kwargs: 可选参数 ty_code | timestamp
        @return:
        """
        query: CoverageInfoModel = None
        ty_code: str = kwargs.get('ty_code', None)
        ty_timestamp: str = kwargs.get('timestamp', None)
        if id not in [DEFAULT_NULL_KEY]:
            query = CoverageInfoModel.objects.filter(id=id)
        else:
            query = CoverageInfoModel.objects
        if ty_code:
            query = query.filter(ty_code=ty_code)
        if ty_timestamp:
            query = query.filter(timestamp=ty_timestamp)

        return query.first()

    def _query_tif(self, **kwargs) -> ForecastTifModel:
        gcid: int = kwargs.get('gcid')
        ty_code: str = kwargs.get('ty_code')
        ty_timestamp: str = kwargs.get('timestamp')

        query = ForecastTifModel.objects.filter(gcid=gcid, ty_code=ty_code, timestamp=ty_timestamp)
        res: CoverageInfoModel = None
        if len(query) > 0:
            res = query.first()
        return res

    def get_tif_url(self, request: Request, **kwargs) -> str:
        """
             获取指定的 tif url
        @param request: 可选参数 ty_code | timestamp
        @return:
        """
        ty_code = kwargs.get('ty_code', None)
        ty_timestamp = kwargs.get('timestamp', None)
        query_coverage: CoverageInfoModel = self.get_coverage(ty_code=ty_code, timestamp=ty_timestamp)
        # 获取 coverage_id 作为 tb:tif 的 gcid
        coverage_id: int = query_coverage.id
        res_tif: ForecastTifModel = self._query_tif(gcid=coverage_id, ty_code=ty_code, timestamp=ty_timestamp)

        store_url: str = STORE_OPTIONS.get('URL')
        store_host: int = STORE_OPTIONS.get('HOST')
        store_common_base: str = STORE_OPTIONS.get('STORE_COMMON_BASE')
        store_head: str = STORE_OPTIONS.get('HEAD')
        url_base = f'http://{store_url}:{store_host}/{store_common_base}/{store_head}'
        url_file = None
        if query_coverage is not None:
            file_full_name: str = f'{res_tif.file_name}.{res_tif.file_ext}'
            url_file = str(pathlib.Path(res_tif.relative_path) / file_full_name)
        else:
            raise NoneError(f'ty_code:{ty_code}|ty_timestamp:{ty_timestamp} 查无结果')
        url_full = f'{url_base}/{url_file}'
        return url_full
