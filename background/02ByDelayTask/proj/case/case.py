#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/13 22:05
# @Author  : evaseemefly
# @Desc    : 用来放置 各类测试样例
# @Site    :
# @File    : case.py
# @Software: PyCharm
from typing import List, Union
import pathlib
from datetime import datetime, timedelta
from core.data import GroupTyphoonPath, get_match_files, to_ty_group, to_station_realdata, get_gp, to_ty_field_surge, \
    to_ty_pro_surge, to_ty_detail, to_ty_task_rela, to_ty_max_surge
from model.models import TyphoonForecastDetailModel
from core.file import StationSurgeRealDataFile
from common.enum import ForecastOrganizationEnum, TyphoonForecastSourceEnum
from common.const import UNLESS_INDEX, UNLESS_ID_STR, NONE_ID
from task.jobs import JobGetTyDetail, JobGetCustomerTyDetail, JobGeneratePathFile, JobTxt2Nc, JobTxt2NcPro, JobTaskBatch
from conf.settings import TEST_ENV_SETTINGS
from local.globals import get_celery
from task.celery import app
from util.customer_decorators import store_job_rate
from util.log import Loggings, log_in
# 分表相关
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData, Table
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, text
from sqlalchemy.dialects.mysql import DATETIME, INTEGER, TINYINT, VARCHAR
#
from core.db import DbFactory

from util.customer_decorators import log_count_time, store_job_rate
from common.enum import JobInstanceEnum, TaskStateEnum, ForecastAreaEnum

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
    dir_path: str = str(pathlib.Path(ROOT_DIR) / 'pathfiles' / ty_stamp_str)
    # GroupTyphoonPath(TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR'), '2022', '2020042710').read_forecast_data()
    list_match_files: List[str] = get_match_files('^[A-Z]+\d+_\d+_[a-z]{1}\d{1}_[a-z]{1}_?\d+',
                                                  dir_path)
    # ty_detail: TyphoonForecastDetailModel = to_ty_detail(ty_detail)
    ty_id: int = to_ty_group(list_match_files, ty_detail=ty_detail)
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


def case_station(start: datetime, end: datetime, ty_code: str, ty_timestamp_str: str, ty_id=UNLESS_INDEX,
                 forecast_area=None):
    """
        批量写入 station 的 case
    @param start:
    @param end:
    @param ty_code:
    @param ty_timestamp_str: 1642658538 创建案例的时间戳字符串
    @param ty_id:
    @param forecast_area:
    @return:
    """
    # TODO:[-] 21-07-20 注意此处的 path_marking 手动指定为 0即可，或者去掉也可以
    query_gp = get_gp(ty_code=ty_code, ts=ty_timestamp_str, path_type='c', path_marking=0, bp=0,
                      is_increase=True)
    # gmt_start = datetime(2020, 9, 15, 17)
    # gmt_end = datetime(2020, 9, 18, 0)
    gmt_start = start
    gmt_end = end  # 目前使用的结束时间为从台风网上爬取的时间的结束时间(预报)
    ty_stamp: str = f'TY{ty_code}_{ty_timestamp_str}'  # TY2046_1642658538
    ty_detail: TyphoonForecastDetailModel = TyphoonForecastDetailModel(code=TY_CODE,
                                                                       organ_code=ForecastOrganizationEnum.NMEFC.value,
                                                                       gmt_start=gmt_start,
                                                                       gmt_end=gmt_end,
                                                                       forecast_source=TyphoonForecastSourceEnum.DEFAULT.value,
                                                                       id=ty_id)
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
    dir_path: str = str(pathlib.Path(ROOT_DIR) / 'result' / ty_stamp)
    if len(query_gp) > 0:
        target_gp = query_gp[0]
    # TODO:[*] 21-07-20 注意此处，由于有可能存在非台风的编号，也就是例如 TD04 这种是，所以不能直接匹配多个数字
    # old: Surge_TY2022_2021010416_c0_p_10.dat

    # new: Surge_TYTD04_2021071908_f6_p_05.dat
    list_match_files: List[str] = get_match_files('^Surge_[A-Z]+\d+_\d+_[a-z]{1}\d{1}_[a-z]{1}_?\d+.dat',
                                                  dir_path)
    to_station_realdata(list_match_files, ty_detail, forecast_dt_start=forecast_dt_start, ty_id=ty_id,
                        forecast_area=forecast_area)
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
    dir_path: str = str(pathlib.Path(ROOT_DIR) / 'result' / ty_stamp)
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
    dir_path: str = str(pathlib.Path(ROOT_DIR) / 'result' / ty_stamp)
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


def case_max_surge(ty_code: str, ty_stamp: str, gmt_start: datetime, gmt_end: datetime):
    """
        最大增水场
    @param ty_code:
    @param ty_stamp:
    @param gmt_start:
    @param gmt_end:
    @return:
    """
    # 概率场的正则匹配表达式
    # TODO:[-] 此处注意若再次执行时会出现 xxx_converted.nc的文件，需要忽略，所以加入了 xxm.nc 的正则，忽略了m_converted.nc 这种已经转换后的文件
    re_str: str = '^maxSurge\w*p00.nc'
    dir_path: str = str(pathlib.Path(ROOT_DIR) / 'result' / ty_stamp)
    list_match_files: List[str] = get_match_files(re_str, dir_path)
    ty_detail: TyphoonForecastDetailModel = TyphoonForecastDetailModel(code=ty_code,
                                                                       organ_code=ForecastOrganizationEnum.NMEFC.value,
                                                                       gmt_start=gmt_start,
                                                                       gmt_end=gmt_end,
                                                                       forecast_source=TyphoonForecastSourceEnum.DEFAULT.value,
                                                                       timestamp=TY_TIMESTAMP)
    # 注意此处会包含 _converted.nc 的文件需要剔除该文件
    filter_list_files: List[str] = list_match_files
    to_ty_max_surge(filter_list_files, dir_path=dir_path, gmt_start=gmt_start)
    pass


def case_db_splittable():
    auto_base = automap_base()

    db_factory = DbFactory()
    session = db_factory.Session
    engine = db_factory.engine
    auto_base.prepare(engine, reflect=True)
    table_name: str = 'station_info'
    station_info = getattr(auto_base.classes, table_name)

    # station_info=auto_base.classes.station_info
    query = session.query(station_info).filter_by(code='GTO').all()
    pass


def case_db_check_tab_exist(tab_name: str):
    """
        判断指定表是否存在
    @return:
    """
    is_exist = False
    auto_base = automap_base()

    db_factory = DbFactory()
    session = db_factory.Session
    engine = db_factory.engine
    auto_base.prepare(engine, reflect=True)
    list_tabs = auto_base.classes
    if tab_name in list_tabs:
        is_exist = True
    # station_info = getattr(auto_base.classes, table_name)
    return is_exist
    pass


def case_db_create_split_tab(ty_code: str):
    """
        测试分表插入
    @param item:
    @return:
    """
    db_name: str = 'typhoon_forecast_db_new'
    tab_name: str = f'station_forecast_realdata_{ty_code}'
    # 注意此处需要先判断是否已经存在指定的 tb
    # 方式1: 执行sql语句创建 tb —— 不使用此种方式
    sql_str: str = f""""
    create table {db_name}.{tab_name}
    (
        id           int auto_increment
            primary key,
        is_del       tinyint(1)   not null,
        gmt_created  datetime(6)  null,
        gmt_modified datetime(6)  null,
        name         varchar(200) not null,
        code         varchar(50)  not null,
        lat          double       null,
        lon          double       null,
        `desc`       varchar(500) null,
        is_abs       tinyint(1)   not null,
        pid          int          not null
    );"""
    # 方式2: 不使用执行 create sql
    meta_data = MetaData()
    Table(tab_name, meta_data, Column('id', Integer, primary_key=True),
          Column('is_del', TINYINT(1), nullable=False, server_default=text("'0'"), default=0),

          Column('ty_code', VARCHAR(200), nullable=False),
          Column('gp_id', Integer, nullable=False),
          Column('station_code', VARCHAR(200), nullable=False),
          Column('forecast_dt', DATETIME(fsp=2)),
          Column('forecast_index', Integer, nullable=False),
          Column('surge', Float, nullable=False),
          Column('timestamp', VARCHAR(100), nullable=False),
          Column('gmt_created', DATETIME(fsp=6), default=datetime.utcnow),
          Column('gmt_modified', DATETIME(fsp=6), default=datetime.utcnow)
          )
    db_factory = DbFactory()
    session = db_factory.Session
    engine = db_factory.engine
    with engine.connect() as conn:
        # result_proxy = conn.execute(sql_str)
        # result = result_proxy.fetchall()
        try:
            meta_data.create_all(engine)
        except Exception as ex:
            print(ex.args)


def case_db_insert_split_tab(ty_code: str):
    db_name: str = 'typhoon_forecast_db_new'
    tab_name: str = f'station_forecast_realdata_{ty_code}'
    auto_base = automap_base()
    db_factory = DbFactory()
    engine = db_factory.engine
    auto_base.prepare(engine, reflect=True)
    StationSurgeDao = getattr(auto_base.classes, tab_name)
    station_model = StationSurgeDao(ty_code='2017', gp_id=0,
                                    station_code='123', forecast_dt=datetime.utcnow(),
                                    forecast_index=1, surge=2.5,
                                    timestamp=datetime.timestamp)
    session = db_factory.Session
    session.add(station_model)
    session.commit()


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

    is_break: bool = False
    if is_break:
        return
    # + 21-09-18 获取传过来的提交参数
    post_data: dict = kwargs
    ty_code: str = post_data.get('ty_code', None)
    post_data_max_wind_radius_diff: int = post_data.get('max_wind_radius_diff')
    post_data_members_num: int = post_data.get('members_num')
    post_data_deviation_radius_list: List[any] = post_data.get('deviation_radius_list')
    is_customer_ty: bool = post_data.get('is_customer_ty', False)
    forecast_area_val: int = post_data.get('forecast_area', ForecastAreaEnum.SCS.value)
    forecast_area: ForecastAreaEnum = ForecastAreaEnum(forecast_area_val)
    # TODO:[-] 21-12-02 获取 django 传入的 时间戳
    timestamp: int = post_data.get('timestamp')
    timestamp_str: str = str(timestamp)
    # - 21-09-21
    # 原始正常的 数组
    # ['TYtd03_2021071606_CMA_original',                LIST[0] * 需要加上
    #   ['2021070805', '2021070811', '2021070817'],     LIST[1]
    #   ['106.3', '104.7', '103.2'],                    LIST[2]
    #   ['19.5', '19.7', '19.9'],                       LIST[3]
    #   ['1000', '1002', '1004'],                       LIST[4] 气压
    #   ['15', '12', '10'],                             LIST[5] * 风速
    #   'TD03',                                         LIST[6] * 需要加上
    #   None]                                           LIST[7]
    # - 21-09-21
    # 'customer_ty_cma_list':
    #  list[0] TY2112_2021090116_CMA_original 是具体的编号
    #  List[1] ['2021082314', '2021082320'] 时间 注意传入的是 local 时间，而非 utc 时间,切记！
    #  list[2] ['125.3', '126.6'] 经度
    #  list[3] ['31.3', '33.8']   维度
    #  list[4] ['998', '998']     气压
    #  list[5] ['15', '15']       暂时不用
    # 21-10-22 注意传入的是 local 时间，而非 utc 时间,切记！
    ty_customer_cma: List[List[any]] = []

    if is_customer_ty:
        # 注意传入的 list 为 6位，需要手动添加一个 None 至末尾
        ty_customer_cma = post_data.get('ty_customer_cma', [])
        # ty_customer_cma.append(ty_code)
        # ty_customer_cma.append(None)
    # ty_code: str = '2114'
    if ty_code is None:
        return
    job_ty: Union[JobGetTyDetail, JobGetCustomerTyDetail, None] = None
    if is_customer_ty:
        job_ty = JobGetCustomerTyDetail(ty_code, timestamp_str)
        pass
    else:
        job_ty = JobGetTyDetail(ty_code, timestamp_str)
    # TDOO:[*] 21-10-21 注意需此处爬取后的台风时间为 local ，而django传递过来的为utc时间
    job_ty.to_do(list_customer_cma=ty_customer_cma)
    log_in.info(
        f'获取提交:ty_code:{ty_code}|timestamp:{job_ty.timestamp_str}|forecast_start_utc:{job_ty.forecast_start_dt_utc}|forecast_end_utc:{job_ty.forecast_end_dt_utc}|集合预报路径条数:{post_data_members_num}')
    if len(job_ty.list_cmd) == 0:
        log_in.error(f'获取提交:ty_code:{ty_code}|timestamp:{job_ty.timestamp_str},未爬取到或自定义台风路径为空')
        return
    if len(job_ty.list_cmd) > 0:
        dt_forecast_start: datetime = job_ty.forecast_start_dt_utc
        dt_forecast_end: datetime = job_ty.forecast_end_dt_utc
        timestamp_str: str = job_ty.timestamp_str
        # step 1-2: 生成 pathfile 与 批处理文件
        list_cmd = job_ty.list_cmd
        ty_stamp: str = job_ty.ty_stamp  # TY2109_2021080415
        ty_timestamp: str = job_ty.timestamp_str  # 2021080415
        job_generate = JobGeneratePathFile(ty_code, timestamp_str, list_cmd)
        # + 21-09-18 此处修改为传入的参数为动态的，有 celery 传入
        job_generate.to_do(max_wind_radius_diff=post_data_max_wind_radius_diff, members_num=post_data_members_num,
                           deviation_radius_list=post_data_deviation_radius_list,
                           forecast_area=forecast_area)
        log_in.info(f'ty_code:{ty_code}|timestamp:{job_ty.timestamp_str},生成对应pathfiles+批处理文件')
        # step 1-3: 将爬取到的台风基础信息入库
        # test_ty_stamp = 'TY2142_1632623874'
        ty_detail: TyphoonForecastDetailModel = case_ty_detail(dt_forecast_start, dt_forecast_end, ty_code,
                                                               timestamp_str,
                                                               ty_stamp)

        # step 1-4: 将生成的 grouppath 批量入库
        case_group_ty_path(dt_forecast_start, dt_forecast_end, ty_code, timestamp_str,
                           ty_stamp, ty_detail)
        log_in.info(f'ty_code:{ty_code}|timestamp:{job_ty.timestamp_str},完成grouppath入库步骤')
        ty_id: int = ty_detail.id
        # ------

        # step-2: 执行批处理 调用模型——暂时跳过
        job_task = JobTaskBatch(ty_code, timestamp_str)
        log_in.info(f'ty_code:{ty_code}|timestamp:{job_ty.timestamp_str},提交gpu进行计算！new')
        job_task.to_do(full_path_controlfile=job_generate.full_path_controlfile, members_num=post_data_members_num)
        log_in.info(f'ty_code:{ty_code}|timestamp:{job_ty.timestamp_str},gpu计算结束！new')
        # -----
        # step 3: 处理海洋站
        # 注意 此处的 ty_id 由 case_group_ty_path 处理后创建的一个 ty id
        # TODO:[*] 21-09-09 注意此处的 ty_id 是写死的!
        # !! 测试使用，测试后注释掉
        # timestamp_str: str = '1632639075'
        # ty_stamp: str = 'TY2144_1632639075'
        # ty_id: int = 62
        if not is_debug:
            case_station(dt_forecast_start, dt_forecast_end, ty_code, ty_timestamp, ty_id=ty_id,
                         forecast_area=forecast_area)
            log_in.info(f'ty_code:{ty_code}|timestamp:{job_ty.timestamp_str},完成海洋站数据入库')
            # # # step-3:
            # # TODO:[-] + 21-09-02 txt -> nc 目前没问题，需要注意一下当前传入的 时间戳是 yyyymmddHH 的格式，与上面的不同
            # TODO:[*] 21-09-08 注意此处暂时将 时间戳设置为一个固定值！！注意！！
            job_txt2nc = JobTxt2Nc(ty_code, timestamp_str)
            job_txt2nc.to_do(forecast_start_dt=dt_forecast_start)
            # TODO:[-] 21-11-16 加入了处理最大增水场的步骤！
            case_max_surge(ty_code, ty_stamp, dt_forecast_start, dt_forecast_end)
            log_in.info(f'ty_code:{ty_code}|timestamp:{job_ty.timestamp_str},完成surge_max的.dat->.nc的转换')
            # # # step 3-1:
            # # # # TODO:[*] 21-09-08 注意此处暂时将 ty_stamp 设置为一个固定值！！注意！！上线后要替换为:job_ty.ty_stamp
            case_field_surge(ty_code, ty_stamp, dt_forecast_start, dt_forecast_end)
            log_in.info(f'ty_code:{ty_code}|timestamp:{job_ty.timestamp_str},完成surge_field的.nc->.tiff的转换')
            # # step 3-2:
            # #
            job_txt2ncpro = JobTxt2NcPro(ty_code, timestamp_str)
            job_txt2ncpro.to_do(forecast_start_dt=dt_forecast_start)
            log_in.info(f'ty_code:{ty_code}|timestamp:{job_ty.timestamp_str},完成surge_pro的.dat->.nc的转换')
            case_pro_surge(ty_code, ty_stamp, dt_forecast_start, dt_forecast_end)
            log_in.info(f'ty_code:{ty_code}|timestamp:{job_ty.timestamp_str},完成surge_pro的.nc->.tiff的转换')
    pass


def get_gp_model():
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
    gmt_start = datetime(2020, 9, 17, 21)
    gmt_end = datetime(2020, 9, 19, 3)  # 目前使用的结束时间为从台风网上爬取的时间的结束时间(预报)
    ty_stamp = '1644027304'
    ty_code = '2042'
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
    # to_do()
    # TODO:[-] 22-01-20 测试海洋站 to_store 操作
    # case_station(gmt_start, gmt_end, ty_code, ty_stamp, 80, ForecastAreaEnum.SCS)
    # TODO:[-] 21-09-06 测试 local
    # case_test_local()
    # TODO:[-] 22-05-23 测试分表查询 | 判断指定 tab 是否存在 | 分表写入
    # case_db_splittable()
    # case_db_check_tab_exist('station_info')
    # case_db_create_split_tab('2017')
    case_db_insert_split_tab('2017')
    # 测试查询 gp
    # case_get_gp()
    # test_get_gp_model()
    pass


if __name__ == '__main__':
    main()
