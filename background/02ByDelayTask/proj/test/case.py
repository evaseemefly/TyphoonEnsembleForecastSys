#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/13 22:05
# @Author  : evaseemefly
# @Desc    : 用来放置 各类测试样例
# @Site    :
# @File    : case.py
# @Software: PyCharm

from core.data import GroupTyphoonPath
from conf.settings import TEST_ENV_SETTINGS


def case_group_ty_path():
    """
        + 21-04-13 测试 集合路径
    @return:
    """
    GroupTyphoonPath(TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR'), '2022', '2020042710').read_forecast_data()


def main():
    case_group_ty_path()
    pass


if __name__ == '__main__':
    main()
