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
