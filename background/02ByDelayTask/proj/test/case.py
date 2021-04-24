#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/13 22:05
# @Author  : evaseemefly
# @Desc    : 用来放置 各类测试样例
# @Site    :
# @File    : case.py
# @Software: PyCharm
from typing import List
import pathlib
from core.data import GroupTyphoonPath, get_match_files, to_ty_group, to_station_realdata, get_gp
from model.models import TyphoonForecastDetailModel
from common.enum import ForecastOrganizationEnum, TyphoonForecastSourceEnum
from conf.settings import TEST_ENV_SETTINGS
from datetime import datetime

ROOT_DIR = TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR')


def case_group_ty_path():
    """
        + 21-04-13 测试 集合路径
    @return:
    """
    gmt_start = datetime(2020, 9, 15, 17)
    gmt_end = datetime(2020, 9, 18, 0)
    ty_detail: TyphoonForecastDetailModel = TyphoonForecastDetailModel(code='2022',
                                                                       organ_code=ForecastOrganizationEnum.NMEFC.value,
                                                                       gmt_start=gmt_start,
                                                                       gmt_end=gmt_end,
                                                                       forecast_source=TyphoonForecastSourceEnum.DEFAULT.value)
    dir_path: str = str(pathlib.Path(ROOT_DIR) / 'TY2022_2020042710')
    # GroupTyphoonPath(TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR'), '2022', '2020042710').read_forecast_data()
    list_match_files: List[str] = get_match_files('^[A-Z]+\d+_\d+_[a-z]{1}\d{1}_[a-z]{1}_?\d+',
                                                  dir_path)
    to_ty_group(list_match_files, ty_detail)


def case_station():
    """
        批量写入 station 的 case
    @return:
    """
    query_gp = get_gp(ty_code='2022', ts='2020042710', path_type='c', path_marking=20042710, bp=0, is_increase=True)
    # 对应的 tyGroupPathModel ，主要用来获取 -> id
    target_gp = None
    if len(query_gp) > 0:
        target_gp = query_gp[0]
    pass


def case_get_gp():
    """
        测试 get 指定 gp
    @return:
    """
    query_gp = get_gp(ty_code='2022', ts='2020042710', path_type='c', path_marking=20042710, bp=0, is_increase=True)
    print(query_gp)
    pass


def main():
    # case_group_ty_path()
    # 测试查询 gp
    case_get_gp()
    pass


if __name__ == '__main__':
    main()
