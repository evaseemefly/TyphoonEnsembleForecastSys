#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/15 09:52
# @Author  : evaseemefly
# @Desc    :
# @Site    :
# @File    : enum.py
# @Software: PyCharm

from enum import Enum, unique


@unique
class ForecastOrganizationEnum(Enum):
    NMEFC = 101


@unique
class TyphoonForecastSourceEnum(Enum):
    DEFAULT = 201


@unique
class LayerType(Enum):
    """
        + 21-08-02
        图层枚举
        对应 tb:dict_base -> pid =1100
    """
    MAXSURGECOVERAGE = 1101  # 最大增水场 nc
    MAXSURGETIF = 1102
    FIELDSURGECOVERAGE = 1103  # 诸时场 nc
    FIELDSURGETIF = 1104  # 逐时场的单个时间提取tif
