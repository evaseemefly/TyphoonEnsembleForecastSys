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
from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)

# 本项目中的
from common.view_base import BaseView
from util.const import DEFAULT_NULL_KEY
from .models import CoverageInfoModel, ForecastTifModel
from TyphoonForecastSite.settings import STORE_OPTIONS, STORE_RELATIVE_PATH_OPTIONS
from util.exception import NoneError

from common.interface import ICheckExisted


class RasterBaseView(BaseView):
    def get_coverage(self, id: int = DEFAULT_NULL_KEY, **kwargs) -> CoverageInfoModel:
        """
            获取 对应的 coverage
            注意: 获取 coverage 不需要 forecast_dt
        @param id:
        @param kwargs: 可选参数 ty_code | timestamp
        @return:
        """
        query: CoverageInfoModel = None
        ty_code: str = kwargs.get('ty_code', None)
        ty_timestamp: str = kwargs.get('timestamp', None)
        forecast_dt: datetime = kwargs.get('forecast_dt', None)
        if id not in [DEFAULT_NULL_KEY]:
            query = CoverageInfoModel.objects.filter(id=id)
        else:
            query = CoverageInfoModel.objects
        if ty_code:
            query = query.filter(ty_code=ty_code)
        if ty_timestamp:
            query = query.filter(timestamp=ty_timestamp)
        # if forecast_dt:
        #     query = query.filter(forecast_dt=forecast_dt)

        return query.first()

    def _query_base_tif(self, ty_code: str, ty_timestamp: str) -> QuerySet:
        query: QuerySet = ForecastTifModel.objects.filter(ty_code=ty_code, timestamp=ty_timestamp)
        return query

    def _query_tif(self, **kwargs) -> ForecastTifModel:
        gcid: int = kwargs.get('gcid')
        ty_code: str = kwargs.get('ty_code')
        ty_timestamp: str = kwargs.get('timestamp')
        forecast_dt: datetime = kwargs.get('forecast_dt', None)

        query = self._query_base_tif(ty_code=ty_code, ty_timestamp=ty_timestamp)
        if len(query) > 0:
            query = query.filter(gcid=gcid, forecast_dt=forecast_dt)
        # TODO:[-] 21-07-30 可以去掉 gcid 因为查询时并不需要
        # query = ForecastTifModel.objects.filter(gcid=gcid, ty_code=ty_code, timestamp=ty_timestamp,
        #                                         forecast_dt=forecast_dt)
        res: CoverageInfoModel = None
        if query and len(query) > 0:
            res = query.first()
        return res

    def get_tif_url(self, request: Request, checkCoverage=False, **kwargs) -> str:
        """
             获取指定的 tif url
        @param request: 可选参数 ty_code | timestamp | forecast_dt
        @return:
        """
        ty_code = kwargs.get('ty_code', None)
        ty_timestamp = kwargs.get('timestamp', None)
        coverage_type = kwargs.get('coverage_type')
        # + 21-05-07 新加入的 forecast_dt
        forecast_dt: datetime = kwargs.get('forecast_dt', None)
        query_coverage = None
        if checkCoverage:
            query_coverage: CoverageInfoModel = self.get_coverage(ty_code=ty_code, timestamp=ty_timestamp)
            # 获取 coverage_id 作为 tb:tif 的 gcid
            coverage_id: int = query_coverage.id
        # TODO:[-] 21-07-30 可以去掉 gcid 因为查询时并不需要
        query: QuerySet = self._query_base_tif(ty_code=ty_code, ty_timestamp=ty_timestamp)
        if coverage_type:
            query = query.filter(coverage_type=coverage_type.value)
        res_tif: ForecastTifModel = query.first()
        # res_tif: ForecastTifModel = self._query_tif(gcid=coverage_id, ty_code=ty_code, timestamp=ty_timestamp,
        #                                             forecast_dt=forecast_dt)

        store_url: str = STORE_OPTIONS.get('URL')
        store_host: int = STORE_OPTIONS.get('HOST')
        store_common_base: str = STORE_OPTIONS.get('STORE_COMMON_BASE')
        store_head: str = STORE_OPTIONS.get('HEAD')
        # + 21-08-01 由于不同的数据中间还会继续分层，所以引入了 STORE_RELATIVE_PATH_OPTIONS
        store_relative_path: str = STORE_RELATIVE_PATH_OPTIONS.get('TY_GROUP_CASE')
        url_base = f'http://{store_url}:{store_host}/{store_common_base}/{store_head}/{store_relative_path}/'
        url_file = None
        if res_tif is not None:
            file_full_name: str = f'{res_tif.file_name}.{res_tif.file_ext}'
            url_file = str(pathlib.Path(res_tif.relative_path) / file_full_name)
        else:
            raise NoneError(f'ty_code:{ty_code}|ty_timestamp:{ty_timestamp} 查无结果')
        url_full = f'{url_base}/{url_file}'
        return url_full


class GeoCommonView(ICheckExisted):
    def check_existed(self, ty_code: str, timestamp: str, forecast_dt: datetime) -> bool:
        """
            + 21-05-28
            根据 传入的参数 判断是否存在指定的 栅格数据
        @param ty_code:
        @param timestamp:
        @param forecast_dt:
        @return:
        """
        isExisted: bool = False
        query: QuerySet = ForecastTifModel.objects.filter(ty_code=ty_code, timestamp=timestamp, forecast_dt=forecast_dt)
        if len(query) > 0:
            isExisted: bool = True
        return isExisted
