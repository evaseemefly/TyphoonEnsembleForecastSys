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
from common.models import DictBaseModel
from util.const import DEFAULT_NULL_KEY
from .models import CoverageInfoModel, ForecastTifModel, ForecastProTifModel
from TyphoonForecastSite.settings import STORE_OPTIONS, STORE_RELATIVE_PATH_OPTIONS
from util.customer_exception import NoneError
from util.enum import LayerTypeEnum

from common.interface import ICheckExisted


class RasterBaseView(BaseView):
    # @staticmethod()
    def _get_pro_tif_types_ids(self) -> List[int]:
        """
            获取 概率增水的 coverage_type 数组
        :return:
        """
        ids: List[int] = []
        # [{'code': 1301}, {'code': 1302}, {'code': 1303}, {'code': 1304}]
        ids = DictBaseModel.objects.filter(pid=LayerTypeEnum.SURGE_PRO_COVERAGE.value).values('code')
        ids: List[int] = [temp.get('code') for temp in ids]
        return ids

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

    def _query_pro_tif(self, **kwargs) -> QuerySet:
        ty_code: str = kwargs.get('ty_code')
        ty_timestamp: str = kwargs.get('ty_timestamp')
        pro_val: float = float(kwargs.get('pro'))
        coverage_type = kwargs.get('coverage_type')
        # res_pro_tif: ForecastProTifModel = None
        query: QuerySet = ForecastProTifModel.objects.filter(ty_code=ty_code, timestamp=ty_timestamp,
                                                             coverage_type=coverage_type)
        # if len(query) > 0:
        #     res_pro_tif = query
        return query

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
        pro: datetime = kwargs.get('pro', None)
        query_coverage = None
        if checkCoverage:
            query_coverage: CoverageInfoModel = self.get_coverage(ty_code=ty_code, timestamp=ty_timestamp, pro=pro)
            # 获取 coverage_id 作为 tb:tif 的 gcid
            coverage_id: int = query_coverage.id
        # TODO:[-] 21-07-30 可以去掉 gcid 因为查询时并不需要
        ids_pro_tif_coverage: List[int] = self._get_pro_tif_types_ids()
        query: QuerySet = None
        if coverage_type in ids_pro_tif_coverage:
            # 若为 概率增水场，则只需要查询概率增水场的 tif 即可
            query: QuerySet = self._query_pro_tif(ty_code=ty_code, ty_timestamp=ty_timestamp, pro=pro,
                                                  coverage_type=coverage_type)
        else:
            # 非概率增水场执行以下操作
            query: QuerySet = self._query_base_tif(ty_code=ty_code, ty_timestamp=ty_timestamp)
            if coverage_type:
                query = query.filter(coverage_type=coverage_type.value)
            if forecast_dt:
                query = query.filter(forecast_dt=forecast_dt)
        res_tif: ForecastTifModel = query.first()
        # res_tif: ForecastTifModel = self._query_tif(gcid=coverage_id, ty_code=ty_code, timestamp=ty_timestamp,
        #                                             forecast_dt=forecast_dt)

        store_url: str = STORE_OPTIONS.get('URL')
        store_host: int = STORE_OPTIONS.get('HOST')
        store_common_base: str = STORE_OPTIONS.get('STORE_COMMON_BASE')
        store_head: str = STORE_OPTIONS.get('HEAD')
        store_ty_stamp: str = f'TY{ty_code}_{ty_timestamp}'
        # + 21-08-01 由于不同的数据中间还会继续分层，所以引入了 STORE_RELATIVE_PATH_OPTIONS
        store_relative_path: str = STORE_RELATIVE_PATH_OPTIONS.get('TY_GROUP_CASE')
        # TODO:[*] 21-08-10 此处需要注意，store_relative_path 不包含 /result/ 需要手动在后面加上，暂时手动加上，注意 p5750 的环境
        # TODO:[*] 21-09-08 注意修改 后的新的路径为 E:\05DATA\01nginx_data\nmefc_download\TY_GROUP_RESULT\TY2114_1631066272\result
        # TODO:[-] 21-10-14 上线后的路径修改为 : http://128.5.10.21:82/images/result/TY2097_1634180640/fieldSurge_TY2097_1634180640_c0_p00_202009180100.tif
        # http://localhost:82/images/nmefc_download/TY_GROUP_RESULT//TY2022_2021010416\\proSurge_TY2022_2021010416_gt0_5m.tif
        # TODO:[-] 21-10-14 之前本地的备份
        # url_base = f'http://{store_url}:{store_host}/{store_common_base}/{store_head}/{store_relative_path}/result/{store_ty_stamp}'
        url_base = f'http://{store_url}:{store_host}/{store_common_base}/result/{store_ty_stamp}'
        url_file = None
        if res_tif is not None:
            file_full_name: str = f'{res_tif.file_name}.{res_tif.file_ext}'
            # TODO:[-] 21-08-04 注意实际存储的最后一级的路径是 : xxxx/TY_GROUP_RESULT/TY2022_2021010416/xxxx , 需要加入 TY+ty_code_timestamp
            file_ts_relative_path: str = f'{res_tif.relative_path}'
            url_file = str(pathlib.Path(file_ts_relative_path) / file_full_name)
        else:
            raise NoneError(f'ty_code:{ty_code}|ty_timestamp:{ty_timestamp} 查无结果')
        url_full = f'{url_base}/{file_full_name}'
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
