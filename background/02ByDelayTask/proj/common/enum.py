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
class ForecastAreaEnum(Enum):
    '''
        + 22-01-18
        预报区域枚举
        对应 tb: dict_base
    '''
    BHI = 510  # 一区
    ECS = 511  # 二区
    SCS = 512  # 三区 ,注意三区目前为默认预报区域


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
    PROSURGECOVERAGE = 1105  # 风暴增水概率
    PROSURGECOVERAGEGT05 = 1301  # 增水大于0.5m的概率 nc
    PROSURGECOVERAGEGT10 = 1302
    PROSURGECOVERAGEGT15 = 1303
    PROSURGECOVERAGEGT20 = 1304
    PROSURGECOVERAGEGT25 = 1305
    PROSURGECOVERAGEGT30 = 1306
    PROSURGETIFGT05 = 1311  # 增水大于0.5m的概率 tif
    PROSURGETIFGT10 = 1312
    PROSURGETIFGT15 = 1313
    PROSURGETIFGT20 = 1314
    PROSURGETIFGT25 = 1315
    PROSURGETIFGT30 = 1316


@unique
class TaskStateEnum(Enum):
    '''
        对应的是 user_jobuserrate -> state 以及 user_taskinfo -> state

        # TODO:[*] 20-05-07 此处与枚举 users/models.py -> CHOICE_STATUS 相对应，此处如果处理使 enum -> 元祖
    '''
    RUNNING = 7101
    COMPLETED = 7102
    WAITTING = 7103
    ERROR = 7104
    UNUSED = 7105


@unique
class JobInstanceEnum(Enum):
    INIT_CELERY = 0
    GET_TY_DETAIL = 1
    GEN_PATH_FILES = 2
    GEN_CONTROL_FILES = 3
    STORE_TY_DETAIL = 4  # 存储 获取到的 ty
    STORE_GROUP_PATH = 5
    STORE_STATION = 6
    TASK_BATCH = 7
    TXT_2_NC = 8
    STORE_MAX_SURGE = 9  # 处理最大增水场
    STORE_FIELD_SURGE = 10
    TXT_2_NC_PRO = 11
    STORE_PRO_SURGE = 12
