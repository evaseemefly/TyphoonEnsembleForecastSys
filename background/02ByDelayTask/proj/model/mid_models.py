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
