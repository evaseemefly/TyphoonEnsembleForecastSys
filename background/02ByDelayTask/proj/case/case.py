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
from datetime import datetime, timedelta
from core.data import GroupTyphoonPath, get_match_files, to_ty_group, to_station_realdata, get_gp, to_ty_field_surge, \
    to_ty_pro_surge, to_ty_detail, to_ty_task_rela
from model.models import TyphoonForecastDetailModel
from core.file import StationSurgeRealDataFile
from common.enum import ForecastOrganizationEnum, TyphoonForecastSourceEnum
from common.const import UNLESS_INDEX, UNLESS_ID_STR, NONE_ID
from task.jobs import JobGetTyDetail, JobGeneratePathFile, JobTxt2Nc, JobTxt2NcPro, JobTaskBatch
from conf.settings import TEST_ENV_SETTINGS
from local.globals import get_celery
from task.celery import app
from util.customer_decorators import store_job_rate

from util.customer_decorators import log_count_time, store_job_rate
from common.enum import JobInstanceEnum, TaskStateEnum

ROOT_DIR = TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR')
TY_CODE = TEST_ENV_SETTINGS.get('TY_CODE')
TY_TIMESTAMP = TEST_ENV_SETTINGS.get('TY_TIMESTAMP')
# 'TY2022_2021010416'
TY_STAMP = 'TY' + TY_CODE + "_" + TY_TIMESTAMP


def case_group_ty_path(gmt_start, gmt_end, ty_code: str, timestamp: str, ty_stamp: str,
                       ty_detail: TyphoonForecastDetailModel, *args, **kwargs):
    """
        - 21-09-12 将 处理台风基础信息 放在了 case_ty_detail 中
        将 集合路径批量入库
        返回 ty_id
    @param gmt_start:
    @param gmt_end:
    @param ty_code:
    @param timestamp:
    @param ty_stamp:
    @param ty_detail: 只需要 ty_detail.ty_id
    @param args:
    @param kwargs:
    @return:
    """
    # todo:[*] 21-07-19 使用 TD04 编号的热带风暴 作为输入的台风
    # gmt_start = datetime(2020, 9, 15, 17)
    # gmt_end = datetime(2020, 9, 18, 0)
    # TODO:[*] 21-09-06 需要加入 celery-id 相当于是作业 id
    celery_id: str = kwargs.get('celery_id', UNLESS_ID_STR)
    ty_stamp_str: str = ty_stamp
    # ty_detail: TyphoonForecastDetailModel = TyphoonForecastDetailModel(code=ty_code,
    #                                                                    organ_code=ForecastOrganizationEnum.NMEFC.value,
    #                                                                    gmt_start=gmt_start,
    #                                                                    gmt_end=gmt_end,
    #                                                                    forecast_source=TyphoonForecastSourceEnum.DEFAULT.value,
    #                                                                    timestamp=timestamp)

    #  21-07-19 之前的路径
    # dir_path: str = str(pathlib.Path(ROOT_DIR) / ty_timestamp / 'GROUP')
    # TODO:[*] 21-07-19 更新后的适配当前存储路径的路径
    dir_path: str = str(pathlib.Path(ROOT_DIR) / ty_stamp_str / 'pathfiles')
    # GroupTyphoonPath(TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR'), '2022', '2020042710').read_forecast_data()
    list_match_files: List[str] = get_match_files('^[A-Z]+\d+_\d+_[a-z]{1}\d{1}_[a-z]{1}_?\d+',
                                                  dir_path)
    # ty_detail: TyphoonForecastDetailModel = to_ty_detail(ty_detail)
    ty_id: int = to_ty_group(list_match_files, ty_detail)
    return ty_id


def case_ty_detail(gmt_start, gmt_end, ty_code: str, timestamp: str, ty_stamp: str, *args,
                   **kwargs) -> TyphoonForecastDetailModel:
    """
        + 21-09-12 加入的执行 写入 基础台风信息的 步骤
    @param gmt_start: 起始时间(utc)
    @param gmt_end:   结束时间(utc)
    @param ty_code:   台风编号
    @param timestamp: 创建台风时间戳
    @param ty_stamp:  台风编号+时间戳
    @param args:
    @param kwargs:
    @return:
    """
    ty_detail: TyphoonForecastDetailModel = TyphoonForecastDetailModel(code=ty_code,
                                                                       organ_code=ForecastOrganizationEnum.NMEFC.value,
                                                                       gmt_start=gmt_start,
                                                                       gmt_end=gmt_end,
                                                                       forecast_source=TyphoonForecastSourceEnum.DEFAULT.value,
                                                                       timestamp=timestamp)

    ty_detail: TyphoonForecastDetailModel = to_ty_detail(ty_detail)
    # + 21-09-14 写入 ty 与 task 的关联表
    to_ty_task_rela(ty_detail.id)
    return ty_detail


def case_station(start: datetime, end: datetime, ty_stamp: str, ty_id=UNLESS_INDEX):
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
    # ty_timestamp: str = TY_STAMP
    ty_id: int = ty_id if ty_id != UNLESS_INDEX else 8
    # ty_id: int = 8
    # TODO:[*] 21-07-20 注意此处需要修改为明杰的存储规则
    # EG:     'E:\\02data\\05docker-data\\docker-shared\\ty_docker\\TYTD04_2021071908\\STATION'
    # 实际地址: E:\02data\05docker-data\docker-shared\ty_docker\result\TYTD04_2021071908
    # 21-09-09 此处路径修改为 : D:\05DATA\NGINX_DATA\nmefc_download\TY_GROUP_RESULT\TY2114_1631180476\result
    dir_path: str = str(pathlib.Path(ROOT_DIR) / ty_stamp / 'result')
    if len(query_gp) > 0:
        target_gp = query_gp[0]
    # TODO:[*] 21-07-20 注意此处，由于有可能存在非台风的编号，也就是例如 TD04 这种是，所以不能直接匹配多个数字
    # old: Surge_TY2022_2021010416_c0_p_10.dat
    # new: Surge_TYTD04_2021071908_f6_p_05.dat
    list_match_files: List[str] = get_match_files('^Surge_[A-Z]+\d+_\d+_[a-z]{1}\d{1}_[a-z]{1}_?\d+.dat',
                                                  dir_path)
    to_station_realdata(list_match_files, ty_detail, forecast_dt_start=forecast_dt_start, ty_id=ty_id)
    pass


def case_field_surge(ty_code: str, ty_stamp: str, gmt_start: datetime, gmt_end: datetime):
    """
        处理对应台风+时间戳的逐时风暴增水
    @param ty_code:
    @param ty_stamp:
    @param gmt_start:
    @param gmt_end:
    @return:
    """
    re_str: str = '^field\w*.nc'
    dir_path: str = str(pathlib.Path(ROOT_DIR) / ty_stamp / 'result')
    list_match_files: List[str] = get_match_files(re_str, dir_path)
    ty_detail: TyphoonForecastDetailModel = TyphoonForecastDetailModel(code=TY_CODE,
                                                                       organ_code=ForecastOrganizationEnum.NMEFC.value,
                                                                       gmt_start=gmt_start,
                                                                       gmt_end=gmt_end,
                                                                       forecast_source=TyphoonForecastSourceEnum.DEFAULT.value,
                                                                       timestamp=TY_TIMESTAMP)
    # 注意此处会包含 _converted.nc 的文件需要剔除该文件
    filter_list_files: List[str] = [file
                                    for file in list_match_files if file.find('converted') < 0]
    to_ty_field_surge(filter_list_files, dir_path=dir_path, gmt_start=gmt_start)
    pass


def case_pro_surge(ty_code: str, ty_stamp: str, gmt_start: datetime, gmt_end: datetime):
    """
        概率增水场
    @param ty_code:
    @param ty_stamp:
    @param gmt_start:
    @param gmt_end:
    @return:
    """
    # 概率场的正则匹配表达式
    # TODO:[-] 此处注意若再次执行时会出现 xxx_converted.nc的文件，需要忽略，所以加入了 xxm.nc 的正则，忽略了m_converted.nc 这种已经转换后的文件
    re_str: str = '^proSurge\w*m.nc'
    dir_path: str = str(pathlib.Path(ROOT_DIR) / ty_stamp / 'result')
    list_match_files: List[str] = get_match_files(re_str, dir_path)
    ty_detail: TyphoonForecastDetailModel = TyphoonForecastDetailModel(code=ty_code,
                                                                       organ_code=ForecastOrganizationEnum.NMEFC.value,
                                                                       gmt_start=gmt_start,
                                                                       gmt_end=gmt_end,
                                                                       forecast_source=TyphoonForecastSourceEnum.DEFAULT.value,
                                                                       timestamp=TY_TIMESTAMP)
    # 注意此处会包含 _converted.nc 的文件需要剔除该文件
    filter_list_files: List[str] = list_match_files
    to_ty_pro_surge(filter_list_files, dir_path=dir_path, gmt_start=gmt_start)
    pass


def case_get_gp():
    """
        测试 get 指定 gp
    @return:
    """
    query_gp = get_gp(ty_code='2022', ts='2020042710', path_type='c', path_marking=20042710, bp=0, is_increase=True)
    print(query_gp)
    pass


def case_job_craw_ty():
    """
        + 21-09-01
        手动抓取台风
    @return:
    """
    job_ty = JobGetTyDetail('2113')
    job_ty.to_do()
    list_cmd = job_ty.list_cmd
    timestamp_str = job_ty.timestamp
    job_generate = JobGeneratePathFile('2112', str(job_ty.timestamp), list_cmd)
    job_generate.to_do()
    # ts_dt:datetime=
    # TODO:[-] + 21-09-02 txt -> nc 目前没问题，需要注意一下当前传入的 时间戳是 yyyymmddHH 的格式，与上面的不同
    job_txt2nc = JobTxt2Nc('2109', '2021080415')
    job_txt2nc.to_do()
    job_txt2ncpro = JobTxt2NcPro('2109', '2021080415')
    job_txt2ncpro.to_do()
    pass


def to_do_celery():
    pass


@app.task(bind=True, name="surge_group_ty")
@store_job_rate(job_instance=JobInstanceEnum.INIT_CELERY, job_rate=0)
def to_do(*args, **kwargs):
    """
        step-1: 爬取 指定台风编号的台风并持久化保存

        step 1-2: 生成 pathfile 与 批处理文件

        step 1-3: 将爬取到的台风基础信息入库 + 21-09-12 (将处理 ty_detail 与 ty_group_path 拆分)

        step 1-4: 将生成的 grouppath 批量入库  + 21-09-12 (将处理 ty_detail 与 ty_group_path 拆分)

        step-2: 执行批处理 调用模型——暂时跳过

        step-3: 处理海洋站

        step-4: 生成 pro 与 field nc文件，并转成tiff

        + 21-09-18：
            eg: kwargs:
                {'ty_code': 'DEFAULT',
                'max_wind_radius_diff': 0,
                'members_num': 145,
                'deviation_radius_list':
                    [{'hours': 96, 'radius': 150},
                    {'hours': 72, 'radius': 120},
                    {'hours': 48, 'radius': 100},
                    {'hours': 24, 'radius': 60}]
                }

    @param args:
    @param kwargs:
    @return:
    """
    # step-1: 爬取 指定台风编号的台风
    is_debug: bool = True
    # + 21-09-18 获取传过来的提交参数
    post_data: dict = kwargs
    ty_code: str = '2114' if is_debug else post_data.get('ty_code', None)
    post_data_max_wind_radius_diff: int = post_data.get('max_wind_radius_diff')
    post_data_members_num: int = post_data.get('members_num')
    post_data_deviation_radius_list: List[any] = post_data.get('deviation_radius_list')
    # ty_code: str = '2114'
    if ty_code is None:
        return

    job_ty = JobGetTyDetail(ty_code)
    job_ty.to_do()
    if len(job_ty.list_cmd) == 0:
        return
    if len(job_ty.list_cmd) > 0:
        dt_forecast_start: datetime = job_ty.forecast_start_dt
        dt_forecast_end: datetime = job_ty.forecast_end_dt
        timestamp_str: str = job_ty.timestamp_str
        # step 1-2: 生成 pathfile 与 批处理文件
        list_cmd = job_ty.list_cmd
        # ty_stamp: str = job_ty.ty_stamp
        job_generate = JobGeneratePathFile(ty_code, timestamp_str, list_cmd)
        # + 21-09-18 此处修改为传入的参数为动态的，有 celery 传入
        job_generate.to_do(max_wind_radius_diff=post_data_max_wind_radius_diff, members_num=post_data_members_num,
                           deviation_radius_list=post_data_deviation_radius_list)
        # step 1-3: 将爬取到的台风基础信息入库
        ty_detail: TyphoonForecastDetailModel = case_ty_detail(dt_forecast_start, dt_forecast_end, ty_code,
                                                               timestamp_str,
                                                               job_generate.ty_stamp)
        # step 1-4: 将生成的 grouppath 批量入库
        ty_id: int = case_group_ty_path(dt_forecast_start, dt_forecast_end, ty_code, timestamp_str,
                                        job_generate.ty_stamp, ty_detail)
        # ------

        # step-2: 执行批处理 调用模型——暂时跳过
        # job_task = JobTaskBatch(ty_code, timestamp_str)
        # job_task.to_do()
        # -----
        # step 3: 处理海洋站
        # 注意 此处的 ty_id 由 case_group_ty_path 处理后创建的一个 ty id
        # TODO:[*] 21-09-09 注意此处的 ty_id 是写死的!
        ty_stamp: str = 'TY2114_1631412277'
        ty_id: int = 47
        case_station(dt_forecast_start, dt_forecast_end, ty_stamp, ty_id=ty_id)
        # # # step-3:
        # # TODO:[-] + 21-09-02 txt -> nc 目前没问题，需要注意一下当前传入的 时间戳是 yyyymmddHH 的格式，与上面的不同
        # TODO:[*] 21-09-08 注意此处暂时将 时间戳设置为一个固定值！！注意！！
        job_txt2nc = JobTxt2Nc(ty_code, timestamp_str)
        job_txt2nc.to_do(forecast_start_dt=dt_forecast_start)
        # # # step 3-1:
        # # # # TODO:[*] 21-09-08 注意此处暂时将 ty_stamp 设置为一个固定值！！注意！！上线后要替换为:job_ty.ty_stamp
        case_field_surge(ty_code, ty_stamp, dt_forecast_start, dt_forecast_end)
        # # step 3-2:
        # #
        job_txt2ncpro = JobTxt2NcPro(ty_code, timestamp_str)
        job_txt2ncpro.to_do(forecast_start_dt=dt_forecast_start)
        case_pro_surge(ty_code, ty_stamp, dt_forecast_start, dt_forecast_end)
    pass


def test_get_gp_model():
    """
        测试 根据 file_name 获取对应的 gp_model
    @return:
    """
    dir_path: str = r'/Users/liusihan/data/typhoon_data/TY2022_2020042710/station'
    file_name: str = 'Surge_TY2022_2021010416_c0_p_05.dat'
    StationSurgeRealDataFile(dir_path=dir_path, file_name=file_name).get_pg()


def case_test_local():
    local_celery = get_celery()
    local_celery.global_celery_id = '123'


def main():
    # TODO:[-] 21-07-27 预报的起始时间，目前使用的是 pathfile -> c0_p00 中的路径起止时间
    # ! 注意时间是 utc 时间，文件里面读取的为 local 时间 ！
    gmt_start = datetime(2020, 9, 15, 9)
    gmt_end = datetime(2020, 9, 17, 9)  # 目前使用的结束时间为从台风网上爬取的时间的结束时间(预报)
    # case_group_ty_path(gmt_start, gmt_end)
    # # 21-04-25 批量处理海洋站潮位数据
    # # 注意 此处的 ty_id 由 case_group_ty_path 处理后创建的一个 ty id
    # case_station(gmt_start, gmt_end, ty_id=12)
    # # TODO:[-] 21-08-02 加入了 测试 逐时风暴增水的 case
    # case_field_surge(TY_CODE, TY_STAMP, gmt_start, gmt_end)
    # # TODO:[-] 21-08-09 加入了 测试 概率增水的 case
    # case_pro_surge(TY_CODE, TY_STAMP, gmt_start, gmt_end)
    # # TODO:[-] 21-09-01 加入了 测试 job相关的 case
    # case_job_craw_ty()
    # TODO:[-] 21-09-03 测试全部整合至 to_do 中
    to_do()
    # TODO:[-] 21-09-06 测试 local
    # case_test_local()
    # 测试查询 gp
    # case_get_gp()
    # test_get_gp_model()
    pass


if __name__ == '__main__':
    main()
