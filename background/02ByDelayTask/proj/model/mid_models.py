#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/13 16:50
# @Author  : evaseemefly
# @Desc    :
# @Site    :
# @File    : mid_models.py
# @Software: PyCharm
from datetime import datetime
from typing import List
from numpy import datetime64


class GroupTyphoonPathMidModel:
    """
        + 21-04-13 台风集合预报路径 中间model
    """

    def __init__(self, current: datetime, coords: List[float], bp: float, radius: float):
        self.current = current
        self.coords = coords
        self.bp = bp
        self.gale_radius = radius


class TyphoonForecastDetailMidModel:
    """
        + 21-04-15 台风基本信息
    """

    def __init__(self, code: str, organ_code: str, gmt_start: datetime, gmt_end: datetime, forecast_source: int,
                 is_forecast: bool = True):
        self.code = code
        self.organ_code = organ_code
        self.gmt_start = gmt_start
        self.gmt_end = gmt_end
        self.source = forecast_source
        self.is_forecast = is_forecast


class StationRealDataMidModel:
    def __init__(self, code: str, organ_code: str, gmt_start: datetime, gmt_end: datetime, forecast_source: int,
                 is_forecast: bool = True):
        self.code = code
        self.organ_code = organ_code
        self.gmt_start = gmt_start
        self.gmt_end = gmt_end
        self.source = forecast_source
        self.is_forecast = is_forecast


class TifFileMidModel:
    def __init__(self, forecast_dt: datetime64, tif_file_full_name: str, full_path: str):
        # <class 'numpy.datetime64'>
        self.forecast_dt_64: datetime64 = forecast_dt
        self.tif_file_full_name = tif_file_full_name
        self.full_path = full_path

    @property
    def file_name(self):
        """
            eg:
        @return:
        """
        return self.tif_file_full_name.split('.')[0]

    @property
    def file_ext(self):
        """
            eg: tif
        @return:
        """
        return self.tif_file_full_name.split('.')[1]

    @property
    def forecast_dt(self) -> datetime:
        """
            将 datetime64[ns] -> datetime
        @return:
        """
        return self.forecast_dt_64.astype('datetime64[s]').astype(datetime)


class TifProFileMidModel:
    def __init__(self, tif_file_full_name: str, full_path: str):
        self.tif_file_full_name = tif_file_full_name
        self.full_path = full_path

    @property
    def file_name(self):
        """
            eg:
        @return:
        """
        return self.tif_file_full_name.split('.')[0]

    @property
    def file_ext(self):
        """
            eg: tif
        @return:
        """
        return self.tif_file_full_name.split('.')[1]
