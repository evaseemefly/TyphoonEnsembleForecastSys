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
