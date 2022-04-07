#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/17 4:30 下午
# @Author  : evaseemefly
# @GithubSit: https://github.com/evaseemefly
# @Site    : 
# @File    : views_base.py
# @Software: PyCharm
from datetime import datetime, timedelta
from abc import abstractmethod
import http.client
import json
# ---
from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework.request import Request
from django.db.models import Max, Min

from typing import List

import arrow
from arrow.arrow import Arrow

from .mid_models import TyPathMidModel, TyDetailMidModel, TyForecastRealDataMidModel
from .models import TyphoonForecastDetailModel, TyphoonGroupPathModel, TyphoonForecastRealDataModel
from common.view_base import BaseView
from common.interface import ICheckExisted
from util.common import inter


class TyGroupBaseView(BaseView):
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

    def getDateDist(self, ty_group: TyphoonGroupPathModel) -> List[datetime]:
        """
            查询指定 ty_group 的预报时刻
        @param ty_group:
        @return:
        """
        gp_id: int = ty_group.id

        # query: QuerySet = TyphoonForecastRealDataModel.objects.filter(gp_id=gp_id).distinct('forecast_dt')
        query: QuerySet = TyphoonForecastRealDataModel.objects.filter(gp_id=gp_id).order_by().values('forecast_dt')
        # list_dist_dt: List[datetime] = [temp.datetime for temp in query.all()]
        # 注意若使用 mysql 数据库 则无法使用 .distinct('field_name') 只能使用 .distinct()
        # TODO:[*] 21-05-17 ERROR
        # raise NotSupportedError('DISTINCT ON fields is not supported by this database backend')
        list_dist_dt: List[datetime] = [temp.get('forecast_dt') for temp in query.all()]
        return list_dist_dt

    def getDefaultDateRange(self, **kwargs) -> []:
        """
            + 21-05-18 加载默认的时间范围
                       默认的时间范围是 [当前时间的整点时刻,+24hour]
        @param ty_group:
        @return:
        """
        # TODO:[-] 21-05-18 注意此处若直接使用 datetime.utcnow ，生成的 datetime 是不带时区的，返回的json 中格式为
        # "2021-05-18T12:00:00"
        # 而正常的是:"2020-09-15T17:00:00Z"
        now: Arrow = arrow.utcnow()
        start_time: datetime = arrow.Arrow(now.year, now.month, now.day, now.hour, 0).datetime
        end_time: datetime = start_time + timedelta(hours=24)
        return [start_time, end_time]

    def get_ty_dtrange(self, tyCode: str, timestamp: str) -> List[datetime]:
        """
            + 21-08-24
            获取对应 台风编号 | 时间戳 对应的台风的预报起始时间
        """
        query = TyphoonForecastDetailModel.objects.filter(code=tyCode, timestamp=timestamp)
        target_ty: TyphoonForecastDetailModel = None
        dt_range: List[datetime] = []
        if len(query) > 0:
            target_ty = query.first()
        if target_ty is not None:
            dt_range.append(target_ty.gmt_start)
            dt_range.append(target_ty.gmt_end)
        return dt_range


class TyGroupCommonView(ICheckExisted):
    # @staticmethod
    def check_existed(self, ty_code: str, timestamp: str, forecast_dt: datetime) -> bool:
        """
            + 21-05-28
            根据 传入的参数 判断是否存在指定的 台风路径信息
            目前只从 -> tb: ty_forecast_detailinfo 中查找 gmt_start < forecast_dt and gmt_end > forecast_dt
        @param ty_code:
        @param timestamp:
        @param forecast_dt:
        @return:
        """
        isExisted: bool = False
        query_ty_detail: QuerySet = TyphoonForecastDetailModel.objects.filter(code=ty_code, gmt_start__lte=forecast_dt,
                                                                              gmt_end__gte=forecast_dt)
        query_ty_grouppath: QuerySet = TyphoonGroupPathModel.objects.filter(ty_code=ty_code, timestamp=timestamp)
        if len(query_ty_grouppath) > 0 and len(query_ty_detail) > 0:
            list_detial_ids: List[int] = [temp.id for temp in query_ty_detail]
            list_grouppath_tyids: List[int] = [temp.ty_id for temp in query_ty_grouppath]
            if len(inter(list_detial_ids, list_grouppath_tyids)) > 0:
                isExisted = True
        return isExisted


class TySpiderBaseView(BaseView):
    def spider_check_ty_exist(self, ty_code: str) -> TyDetailMidModel:
        """
            测试抓取台风网的数据
        :return:
        """
        baseUrl = 'typhoon.nmc.cn'
        ty_obj: TyDetailMidModel = None
        # -- 方式3 --
        # 参考文章: https://blog.csdn.net/xietansheng/article/details/115557974

        conn = http.client.HTTPConnection(baseUrl)
        conn.request('GET', "/weatherservice/typhoon/jsons/list_default")
        res = conn.getresponse()
        content = res.read().decode('utf-8')
        '''
            typhoon_jsons_list_default(({ "typhoonList":[[2723.....]
                                        }))
        '''
        '''
            { "typhoonList":[[2723.....]
                                        }
        '''
        new_json = '{' + content[29: -3] + '}'

        print(content)
        obj = json.loads(new_json, strict=False)
        # 找到所有台风的集合
        # if obj.hasattr('typhoonList'):
        # 注意判断字典中是否包含指定key,不能使用 hasattr 的方法进行panduan
        # if hasattr(obj, 'typhoonList'):
        if 'typhoonList' in obj.keys():
            list_typhoons = obj['typhoonList']
            for ty_temp in list_typhoons:
                # [2723975, 'nameless', '热带低压', None, '20210022', 20210022, None, 'stop']
                # 根据台风编号找到是否存在对应的台风，并获取台风 英文名(index=1)+中文名(index=2)+台风路径网的id(index=0)
                temp_code: str = ty_temp[4]
                if temp_code == ty_code:
                    temp_id: int = ty_temp[0]
                    temp_name_ch: str = ty_temp[2]
                    temp_name_en: str = ty_temp[1]
                    ty_obj = TyDetailMidModel(ty_code, temp_id, temp_name_en, temp_name_ch)
                    break
                pass
            pass

        return ty_obj

    def spider_get_ty_path(self, ty_id: int, ty_code: str, ty_name_en: str = 'nameless') -> TyPathMidModel:
        """
            + 22-04-05 获取对应的台风路径
        :param ty_id:
        :param ty_code:
        :param ty_name_en:
        :return:
        """
        baseUrl: str = 'typhoon.nmc.cn'
        # http://typhoon.nmc.cn/weatherservice/typhoon/jsons/view_2726099
        # target_url = f'{url}_{ty_id}'
        conn = http.client.HTTPConnection(baseUrl)
        conn.request('GET', f"/weatherservice/typhoon/jsons/view_{str(ty_id)}")
        res = conn.getresponse()
        content = res.read().decode('utf-8')
        index: int = len(f'typhoon_jsons_view_{str(ty_id)}') + 1
        new_json = content[index:-1]

        #    raise JSONDecodeError("Extra data", s, end)
        # json.decoder.JSONDecodeError: Extra data: line 1 column 10 (char 9)
        '''
            typhoon_jsons_view_2726099(
                {"typhoon":
                    [2726099,
                    "NYATOH",
                    "妮亚图",
                    2121,
                    2121,
                    null,
                    "名字来源：马来西亚；意为：一种在东南亚热带雨林环境中生长的树木。",
                    "stop",
                    [
                        [
                    0   2726232,    
                    1    "202111300000",
                    2    1638230400000,  //ts
                    3    "TS",   // ty_type 
                    4    139.2,  // 经度-lon
                    5    12.6,   // 纬度-lat
                    6    998,   // bp
                    7    18,
                    8    "WNW",
                    9    15,
                    10    [...],
                    11   {
                            "BABJ": [
                            [
                                12,
                                "202111300000",
                                137.6,
                                13.2,
                                990,
                                23,
                                "BABJ",
                                "TS"
                            ],...
                            ]
                         }
                        ],
                        ...
                    ]
        '''
        ty_path_obj = json.loads(new_json, strict=False)
        tyPathMidModel: TyPathMidModel = {}
        if 'typhoon' in ty_path_obj.keys():
            ty_group_detail = ty_path_obj['typhoon']

            ty_group_list: [] = ty_group_detail[8]
            ty_realdata_list: [] = []
            for temp_ty_group in ty_group_list:
                forecast_ty_path_list: [] = []
                if 'BABJ' in temp_ty_group[11].keys():
                    '''
                        "BABJ": [
                            [
                              0  12,                hours
                              1  "202111300000",    timestamp
                              2  137.6,             lon
                              3  13.2,              lat
                              4  990,               bp
                              5  23,
                              6  "BABJ",
                              7  "TS"               ty_type
                            ],...
                            ]
                    '''
                    temp_forecast_ty_path_list = temp_ty_group[11]['BABJ']
                    for temp_forecast_ty_path in temp_forecast_ty_path_list:
                        if len(temp_forecast_ty_path) >= 8:
                            # TODO:[-] 22-04-06 注意此处的 timestamp 实际是 utc 时间的 yyyymmddHHMM
                            hours: int = temp_forecast_ty_path[0]
                            forecast_dt_str_utc: str = temp_forecast_ty_path[1]
                            forecast_dt: datetime = arrow.get(forecast_dt_str_utc,
                                                              'YYYYMMDDHHmm').datetime + timedelta(
                                hours=hours)
                            forcast_ts = forecast_dt.timestamp()

                            forecast_ty_path_list.append(
                                TyForecastRealDataMidModel(temp_forecast_ty_path[3], temp_forecast_ty_path[2],
                                                           temp_forecast_ty_path[4], int(forcast_ts),
                                                           temp_forecast_ty_path[7], []))
                            pass

                        pass
                ty_realdata_list.append(
                    TyForecastRealDataMidModel(temp_ty_group[5], temp_ty_group[4], temp_ty_group[6], temp_ty_group[2],
                                               temp_ty_group[3], forecast_ty_path_list))
                pass
            tyPathMidModel = TyPathMidModel(ty_group_detail[0], ty_group_detail[3], ty_group_detail[1],
                                            ty_group_detail[2],
                                            ty_realdata_list)
        return tyPathMidModel
