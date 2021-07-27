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
from core.file import StationSurgeRealDataFile
from common.enum import ForecastOrganizationEnum, TyphoonForecastSourceEnum
from common.const import UNLESS_INDEX
from conf.settings import TEST_ENV_SETTINGS
from datetime import datetime

ROOT_DIR = TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR')
TY_CODE = TEST_ENV_SETTINGS.get('TY_CODE')
TY_TIMESTAMP = TEST_ENV_SETTINGS.get('TY_TIMESTAMP')
# 'TY2022_2021010416'
TY_STAMP = 'TY' + TY_CODE + "_" + TY_TIMESTAMP


def case_group_ty_path(gmt_start, gmt_end):
    """
        + 21-04-13 测试 集合路径
        - 21-07-20 测试通过
    @return:
    """
    # todo:[*] 21-07-19 使用 TD04 编号的热带风暴 作为输入的台风
    # gmt_start = datetime(2020, 9, 15, 17)
    # gmt_end = datetime(2020, 9, 18, 0)

    ty_timestamp: str = TY_STAMP
    ty_detail: TyphoonForecastDetailModel = TyphoonForecastDetailModel(code=TY_CODE,
                                                                       organ_code=ForecastOrganizationEnum.NMEFC.value,
                                                                       gmt_start=gmt_start,
                                                                       gmt_end=gmt_end,
                                                                       forecast_source=TyphoonForecastSourceEnum.DEFAULT.value,
                                                                       timestamp=TY_TIMESTAMP)

    #  21-07-19 之前的路径
    # dir_path: str = str(pathlib.Path(ROOT_DIR) / ty_timestamp / 'GROUP')
    # TODO:[*] 21-07-19 更新后的适配当前存储路径的路径
    dir_path: str = str(pathlib.Path(ROOT_DIR) / 'pathfiles' / ty_timestamp)
    # GroupTyphoonPath(TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR'), '2022', '2020042710').read_forecast_data()
    list_match_files: List[str] = get_match_files('^[A-Z]+\d+_\d+_[a-z]{1}\d{1}_[a-z]{1}_?\d+',
                                                  dir_path)
    to_ty_group(list_match_files, ty_detail)


def case_station(start: datetime, end: datetime, ty_id=UNLESS_INDEX):
    """
        批量写入 station 的 case
    @return:
    """
    # TODO:[-] 21-07-20 注意此处的 path_marking 手动指定为 0即可，或者去掉也可以
    query_gp = get_gp(ty_code=TY_CODE, ts=TY_TIMESTAMP, path_type='c', path_marking=0, bp=0,
                      is_increase=True)
    # gmt_start = datetime(2020, 9, 15, 17)
    # gmt_end = datetime(2020, 9, 18, 0)
    gmt_start = start
    gmt_end = end  # 目前使用的结束时间为从台风网上爬取的时间的结束时间(预报)
    ty_detail: TyphoonForecastDetailModel = TyphoonForecastDetailModel(code=TY_CODE,
                                                                       organ_code=ForecastOrganizationEnum.NMEFC.value,
                                                                       gmt_start=gmt_start,
                                                                       gmt_end=gmt_end,
                                                                       forecast_source=TyphoonForecastSourceEnum.DEFAULT.value)
    # 对应的 tyGroupPathModel ，主要用来获取 -> id
    target_gp = None
    # TODO:[-] 21-07-20 预报起始时间与 gmt_start 相同
    forecast_dt_start: datetime = gmt_start
    ty_timestamp: str = TY_STAMP
    ty_id: int = ty_id if ty_id != UNLESS_INDEX else 8
    # ty_id: int = 8
    # TODO:[*] 21-07-20 注意此处需要修改为明杰的存储规则
    # EG:     'E:\\02data\\05docker-data\\docker-shared\\ty_docker\\TYTD04_2021071908\\STATION'
    # 实际地址: E:\02data\05docker-data\docker-shared\ty_docker\result\TYTD04_2021071908
    dir_path: str = str(pathlib.Path(ROOT_DIR) / 'result' / ty_timestamp)
    if len(query_gp) > 0:
        target_gp = query_gp[0]
    # TODO:[*] 21-07-20 注意此处，由于有可能存在非台风的编号，也就是例如 TD04 这种是，所以不能直接匹配多个数字
    # old: Surge_TY2022_2021010416_c0_p_10.dat
    # new: Surge_TYTD04_2021071908_f6_p_05.dat
    list_match_files: List[str] = get_match_files('^Surge_[A-Z]+\d+_\d+_[a-z]{1}\d{1}_[a-z]{1}_?\d+.dat',
                                                  dir_path)
    to_station_realdata(list_match_files, ty_detail, forecast_dt_start=forecast_dt_start, ty_id=ty_id)
    pass


def case_get_gp():
    """
        测试 get 指定 gp
    @return:
    """
    query_gp = get_gp(ty_code='2022', ts='2020042710', path_type='c', path_marking=20042710, bp=0, is_increase=True)
    print(query_gp)
    pass


def test_get_gp_model():
    """
        测试 根据 file_name 获取对应的 gp_model
    @return:
    """
    dir_path: str = r'/Users/liusihan/data/typhoon_data/TY2022_2020042710/station'
    file_name: str = 'Surge_TY2022_2021010416_c0_p_05.dat'
    StationSurgeRealDataFile(dir_path=dir_path, file_name=file_name).get_pg()


def main():
    # TODO:[-] 21-07-27 预报的起始时间，目前使用的是 pathfile -> c0_p00 中的路径起止时间
    gmt_start = datetime(2021, 7, 21, 0)
    gmt_end = datetime(2021, 7, 23, 0)  # 目前使用的结束时间为从台风网上爬取的时间的结束时间(预报)
    # case_group_ty_path(gmt_start, gmt_end)
    # 21-04-25 批量处理海洋站潮位数据
    case_station(gmt_start, gmt_end)
    # 测试查询 gp
    # case_get_gp()
    # test_get_gp_model()
    pass


if __name__ == '__main__':
    main()
