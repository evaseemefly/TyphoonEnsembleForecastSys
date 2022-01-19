#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/13 16:50
# @Author  : evaseemefly
# @Desc    : 用来放置 各类处理 data 的实现类
# @Site    :
# @File    : data.py
# @Software: PyCharm
import os
import re
from abc import ABCMeta, abstractclassmethod, abstractmethod, ABC
import pathlib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import arrow
from typing import List
import xarray as xar
import rioxarray
# sqlaclemy
# from sqlalchemy import Query

from model.mid_models import GroupTyphoonPathMidModel, TyphoonForecastDetailMidModel, TifFileMidModel, \
    TifProFileMidModel
from model.models import TyphoonGroupPathModel, TyphoonForecastDetailModel, TyphoonForecastRealDataModel, \
    StationForecastRealDataModel, CoverageInfoModel, ForecastTifModel, ForecastProTifModel, RelaTyTaskModel
from common.const import UNLESS_CODE, UNLESS_RANGE, NONE_ID
from common.common_dict import DICT_STATION, get_area_dict_station
from common.enum import LayerType, ForecastAreaEnum
from local.globals import get_celery

from util.customer_decorators import log_count_time, store_job_rate
from util.log import Loggings, log_in
from common.enum import JobInstanceEnum, TaskStateEnum

from conf.settings import TEST_ENV_SETTINGS
from core.db import DbFactory

from core.file import StationSurgeRealDataFile, FieldSurgeCoverageFile, ProSurgeCoverageFile, MaxSurgeCoverageFile

# root 的根目录
ROOT_PATH = TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR')
YEAR_HEADER: str = TEST_ENV_SETTINGS.get('YEAR_HEADER')


def get_match_files(re_str: str, dir_path: str = None) -> List[str]:
    """
        获取指定路径下 符合正则表达式的 files_list
    @param dir_path: 注意 dir_path 应该是 ROOT_PATH/台风code_timestamp/
    @return:
    """
    list_files: List[str] = []
    if dir_path:
        # 'E:\\01data\\01docker-data\\05container-shared-data\\01docker-ty\\pathfiles\\TYTD04_2021071908\\GROUP'
        target_path = dir_path
        # TODO:[8] 21-07-20 此处需要加入抛出异常
        if pathlib.Path(dir_path).is_dir():
            for file_name in os.listdir(target_path):
                pattern = re.compile(re_str)
                if re.match(pattern, file_name):
                    list_files.append(file_name)
    return list_files


@store_job_rate(job_instance=JobInstanceEnum.STORE_GROUP_PATH, job_rate=35)
def to_ty_detail(ty_detail: TyphoonForecastDetailModel, **kwargs) -> TyphoonForecastDetailModel:
    # ty_id: int = NONE_ID
    session = DbFactory().Session
    session.add(ty_detail)
    session.commit()
    ty_id: int = NONE_ID if ty_detail.id is None else ty_detail.id
    ty_detail.id = ty_id
    return ty_detail


def to_ty_task_rela(ty_id: int, celery_id: int = None, **kwargs) -> bool:
    """
        + 21-09-14 写入 ty 与 task 的关联关系
    @param ty_id:
    @param celery_id:
    @param kwargs:
    @return:
    """
    is_ok: bool = False
    # 获取当前进程的 celery_id
    celery_id: int = get_celery().celery_id if celery_id is None else celery_id
    try:
        session = DbFactory().Session
        rela_task_ty = RelaTyTaskModel(ty_id=ty_id, celery_id=celery_id)
        session.add(rela_task_ty)
        session.commit()
        is_ok = True
    except Exception as ex:
        log_in.error(ex.args)
        # print(ex.args)
    return is_ok


@store_job_rate(job_instance=JobInstanceEnum.STORE_GROUP_PATH, job_rate=40)
def to_ty_group(list_files: List[str], ty_detail: TyphoonForecastDetailModel, **kwargs) -> int:
    """
        将 ty基础信息 入库，并将集合路径批量入库
        返回 ty_id
    @param list_files:
    @param ty_detail:
    @param kwargs: parent_stamp: 传入的是 外侧存储目录的 时间戳字符串
    @return: 返回 ty_id
    """
    ty_id: int = NONE_ID
    parent_stamp_str: str = kwargs.get('parent_stamp', None)
    # ty_detail = kwargs.get('ty_detail', None)
    # 以下暂时注释掉
    # session = DbFactory().Session
    # session.add(ty_detail)
    # session.commit()
    # ty_id = ty_detail.id
    for file_temp in list_files:
        # eg:  TY1822_2020042710_l5_p05
        # eg2: TY1822_2020042710_c0_p_10
        file_name: str = pathlib.Path(file_temp).name
        name_split: List[str] = file_name.split('_')  # ['TY1822', '2020042710', 'c0', 'p', '10']
        ty_code_stamp: str = name_split[0]  # TY1822
        ts_str: str = parent_stamp_str if parent_stamp_str else name_split[1]  # 2020042710
        path_type_stamp: str = name_split[2]
        # 注意此处需要加入判断，若切分后的 len > 4，说明最后是 p_xx 此种形式
        bp_stamp: str = None
        if len(name_split) > 4:
            bp_stamp: str = f'{name_split[3]}_{name_split[4]}'
        else:
            bp_stamp: str = name_split[3]
        if len(ty_code_stamp) > 2 and ty_code_stamp[:2].lower() == 'ty':
            ty_code: str = ty_code_stamp[2:]  # 1822
            # 创建 台风集合预报路径 类
            # TODO:[*] 21-04-25 注意此处与 case.py -> case_group_ty_path -> dir_path 有歧义
            dir_path: str = str(pathlib.Path(ROOT_PATH))
            ty_group = GroupTyphoonPath(dir_path, file_name, ts_str)
            ty_group.read_forecast_data(file_name=file_name)
            ty_group.to_store(ty_detail=ty_detail)

    return ty_id


@store_job_rate(job_instance=JobInstanceEnum.STORE_MAX_SURGE, job_rate=70)
def to_ty_max_surge(list_files: List[str], **kwargs):
    """
        + 21-11-16 加入了之前缺少的最大增水场 -> tif
    @param list_files:
    @param kwargs:
    @return:
    """
    gmt_start = kwargs.get('gmt_start')
    # eg: fieldSurge_TY2022_2021010416_c0_p00_201809150900.nc
    dir_path: str = kwargs.get('dir_path')
    log_in.info(f"处理{dir_path}路径下的maxsurge.nc文件")
    for file_temp in list_files:
        log_in.info(f"处理maxsurge.nc:{file_temp}文件")
        max_surge_file = MaxSurgeCoverageFile(dir_path, file_temp)
        # 修改此处改为最大增水 dataInfo
        field_surge_data: MaxSurgeDataInfo = MaxSurgeDataInfo(max_surge_file, dir_path)
        field_surge_data.to_do(gmt_start=gmt_start)
        pass
    pass


@store_job_rate(job_instance=JobInstanceEnum.STORE_FIELD_SURGE, job_rate=80)
def to_ty_field_surge(list_files: List[str], **kwargs):
    """
        + 21-08-02 自动化处理诸时场nc的全流程
    @param list_files:
    @param ty_detail:
    @param kwargs: need: gmt_start
    @return:
    """
    gmt_start = kwargs.get('gmt_start')
    # eg: fieldSurge_TY2022_2021010416_c0_p00_201809150900.nc
    dir_path: str = kwargs.get('dir_path')
    for file_temp in list_files:
        field_surge_file = FieldSurgeCoverageFile(dir_path, file_temp)
        field_surge_data: FieldSurgeDataInfo = FieldSurgeDataInfo(field_surge_file, dir_path)
        field_surge_data.to_do(gmt_start=gmt_start)
        pass
    pass


@store_job_rate(job_instance=JobInstanceEnum.STORE_PRO_SURGE, job_rate=100)
def to_ty_pro_surge(list_files: List[str], **kwargs):
    """
        + 21-08-08 自动化处理 概率分布场nc
    @param list_files:
    @param kwargs:
    @return:
    """
    gmt_start = kwargs.get('gmt_start')
    # eg: fieldSurge_TY2022_2021010416_c0_p00_201809150900.nc
    dir_path: str = kwargs.get('dir_path')
    for file_temp in list_files:
        field_surge_file = ProSurgeCoverageFile(dir_path, file_temp)
        field_surge_data: ProSurgeDataInfo = ProSurgeDataInfo(field_surge_file, dir_path)
        field_surge_data.to_do(gmt_start=gmt_start)
        pass
    pass


@store_job_rate(job_instance=JobInstanceEnum.STORE_STATION, job_rate=50)
def to_station_realdata(list_files: List[str], ty_detail: TyphoonForecastDetailModel, **kwargs):
    forecast_dt_start: datetime = kwargs.get('forecast_dt_start')
    ty_id: int = kwargs.get('ty_id')
    forecast_area = kwargs.get('forecast_area', None)
    for file_temp in list_files:
        # eg: Surge_TY2022_2021010416_f0_p10.dat
        # eg2: Surge_TY2022_2021010416_c0_p_10.dat
        file_name_source: str = pathlib.Path(file_temp).name  # Surge_TY2022_2021010416_c0_p_10.dat
        # 先去掉后缀
        file_name = file_name_source.split('.')[0]  # Surge_TY2022_2021010416_c0_p_10
        name_split: List[str] = file_name.split('_')  # ['Surge', 'TY2022', '2021010416', 'f0', 'p10']
        ty_code_stamp: str = name_split[1]  # TY1822
        ts_str: str = name_split[2]  # 2020042710
        path_type_stamp: str = name_split[3]
        # 注意此处需要加入判断，若切分后的 len > 4，说明最后是 p_xx 此种形式
        bp_stamp: str = None
        if len(name_split) > 5:
            # ['Surge', 'TY2022', '2021010416', 'c0', 'p', '10']
            bp_stamp: str = f'{name_split[3]}_{name_split[4]}'
        else:
            # ['Surge', 'TY2022', '2021010416', 'f0', 'p10']
            bp_stamp: str = name_split[4]
        if len(ty_code_stamp) > 2 and ty_code_stamp[:2].lower() == 'ty':
            ty_code: str = ty_code_stamp[2:]  # 1822
            station_surge_file: StationSurgeRealDataFile = StationSurgeRealDataFile(
                str(pathlib.Path(file_temp).parents[0]), str(pathlib.Path(file_temp).name))
            pg = station_surge_file.get_pg(ty_id)
            # 创建 台风集合预报路径 类
            # TODO:[-] 21-04-27 此处需要加入判断 pg 是否为 None
            if pg is not None:

                ty_group = StationRealDataFile(ROOT_PATH, file_name, ts_str, pg.id, forecast_dt_start)
                ty_group.read_forecast_data(file_name=file_name_source, timestamp=ts_str, forecast_area=forecast_area)
                ty_group.to_store(ty_detail=ty_detail)
            else:
                # 若为 None 应抛出异常
                # TODO:[*] 21-04-27 + 缺少抛出异常
                pass


def to_station_statistics(ty_detail: TyphoonForecastDetailModel, **kwargs):
    """
        + TODO:[*] 21-10-27 用来实现生成海洋站 分位数 的方法
    @param ty_detail:
    @param kwargs:
    @return:
    """
    session = DbFactory().Session
    session.query(StationForecastRealDataModel).filter(StationForecastRealDataModel.ty_code == ty_detail.code,
                                                       StationForecastRealDataModel.timestamp == ty_detail.timestamp).group_by(
        StationForecastRealDataModel.station_code).all()
    pass


def get_gp(is_many: bool = True, **kwargs) -> List[TyphoonGroupPathModel]:
    """
        + 21-04-24 根据传入的条件找到对应的 tyGroupPath 数组
        TODO:[*] 21-07-20 注意 params: ts is str， path_marking is int，可以统一为一个参数
    @param kwargs:
    @return:
    """
    ty_code: str = kwargs.get('ty_code')
    ts: str = kwargs.get('ts')
    path_type = kwargs.get('path_type')
    path_marking = kwargs.get('path_marking')
    bp = kwargs.get('bp')
    is_increase = kwargs.get('is_increase')
    session = DbFactory().Session
    query_gp = session.query(TyphoonGroupPathModel).filter(
        TyphoonGroupPathModel.ty_code == ty_code, TyphoonGroupPathModel.timestamp == ts,
        TyphoonGroupPathModel.ty_path_type == path_type,
        TyphoonGroupPathModel.ty_path_marking == path_marking, TyphoonGroupPathModel.bp == bp,
        TyphoonGroupPathModel.is_bp_increase == is_increase)
    # obj_group = session.query(TyphoonGroupPathModel).all()
    # 此处加入判断，若是返回多个则执行 .all 若只获取一个执行 .first
    res: List[TyphoonGroupPathModel] = query_gp.all()
    return res


class IBaseOpt(metaclass=ABCMeta):
    """
        需要子类实现的 抽象父类
    """

    @abstractmethod
    def save_dir_path(self, **kwargs) -> str:
        """
            子类实现的 动态的存储文件的 根目录
        :param kwargs:
        :return:
        """
        pass

    @abstractmethod
    def to_store(self, **kwargs) -> bool:
        """
            需要子类实现的抽象方法: 写入db持久化保存
        :param kwargs:
        :return:
        """
        pass


class ITyphoonPath(IBaseOpt):
    dict_data = {
        'DF': None,
        'TY_PATH': None,  # TyphoonGroupPathModel
        'LIST_TY_REALDATA': []  # TyphoonForecastRealDataModel list
    }

    def __init__(self, root_path: str, file_name: str, timestmap_str: str):
        self.root_path = root_path
        # self.ty_code = ty_code
        self.timestmap = timestmap_str
        self.file_name = file_name  # eg: TY1822_2020042710_l5_p05
        self.list_forecast_data: List[GroupTyphoonPathMidModel] = []
        # 台风集合预报路径的正则
        self.re = '^[A-Z]+\d+_\d+_[a-z]{1}\d{1}_[a-z]{1}_?\d+'
        self.session = DbFactory().Session

    @property
    @abstractmethod
    def name_split(self) -> List[str]:
        pass

    @property
    def relative_path(self) -> str:
        """
            存储 group 集合预报路径的的相对路径
        @return:
        """
        # 台风名称前缀
        ty_prefix = 'TY'
        # TY2022_2020042710
        ty_full_name = f'{ty_prefix}{self.ty_code}_{self.timestmap}'
        return ty_full_name

    @property
    def ty_code(self) -> str:
        """
            获取 台风 code
            TODO:[*] 21-04-23 此处与 GroupTyPath 相同，可去掉
        @return:
        """
        code: str = None
        if len(self.name_split) > 0:
            # TY1822 -> 1822
            code = self.name_split[0][2:]
        return code

    @property
    def ty_timestmap(self) -> str:
        """
            获取 台风的时间戳
        @return:
        """
        ts_str: str = None
        if len(self.name_split) > 1:
            ts_str = self.name_split[1]
        return ts_str

    @property
    def ty_bp_stamp(self) -> str:
        """
            获取 台风 气压 标识
            eg: TY1822_2020042710_l5_p05 -> p05
        @return:
        """
        temp_stamp: str = None
        if len(self.name_split) > 3:
            if len(self.name_split) > 4:
                temp_stamp: str = f'{self.name_split[3]}_{self.name_split[4]}'
            else:
                temp_stamp: str = self.name_split[3]
        return temp_stamp

    @property
    def ty_bp_isIncrease(self) -> bool:
        """
            获取 气压的 是否为增量
            eg: TY1822_2020042710_l5_p05 -> true

        @return:
        """
        stamp: str = '_'
        if self.ty_bp_stamp.find(stamp) >= 0:
            return False
        else:
            return True

    @property
    def ty_bp_val(self) -> int:
        """
            获取 group file 的 偏移气压值
            eg: TY1822_2020042710_l5_p05 -> 05
        @return:
        """
        return int(self.ty_bp_stamp[-2:])

    @property
    def ty_path_stamp(self) -> str:
        """
            获取 台风路径 标志
            eg: TY1822_2020042710_l5_p05 -> l5
        @return:
        """
        path_type: str = None
        if len(self.name_split) > 1:
            path_type = self.name_split[2]
        return path_type

    @property
    def ty_path_type(self) -> str:
        return self.ty_path_stamp[:1].lower()

    @property
    def ty_path_marking(self) -> int:
        return int(self.ty_timestmap[1:])

    @property
    def save_dir_path(self) -> str:
        """

        :param kwargs:
        :return:
        """

        final_path_str = str(pathlib.Path(self.root_path) / self.relative_path)
        return final_path_str

    def get_match_files(self, dir_path: str = None) -> List[str]:
        """
            获取指定路径下 符合正则表达式的 files_list
        @param dir_path:
        @return:
        """
        target_path = self.save_dir_path
        list_files: List[str] = []
        if dir_path:
            target_path = dir_path
        for file_name in os.listdir(target_path):
            pattern = re.compile(self.re)
            if re.match(pattern, file_name):
                list_files.append(file_name)
        return list_files


class GroupTyphoonPath(IBaseOpt):
    dict_data = {
        'DF': None,
        'TY_PATH': None,  # TyphoonGroupPathModel
        'LIST_TY_REALDATA': []  # TyphoonForecastRealDataModel list
    }

    def __init__(self, root_path: str, file_name: str, timestmap_str: str):
        self.root_path = root_path
        # self.ty_code = ty_code
        self.timestmap = timestmap_str
        self.file_name = file_name  # eg: TY1822_2020042710_l5_p05
        self.list_forecast_data: List[GroupTyphoonPathMidModel] = []
        # 台风集合预报路径的正则
        self.re = '^[A-Z]+\d+_\d+_[a-z]{1}\d{1}_[a-z]{1}_?\d+'
        self.session = DbFactory().Session

    def to_store(self, ty_detail: TyphoonForecastDetailModel, **kwargs) -> bool:
        """
            主要是将与 台风集合预报路径 相关的逻辑 to -> db
            GroupTYphoonPathModel + ForecastTyphoonDataModel
        @param ty_detail: 台风基本信息，主要包含台风 id
        @param kwargs:
        @return:
        """
        is_stored = False
        if self.dict_data['TY_PATH']:
            ty_group_path: TyphoonGroupPathModel = self.dict_data.get('TY_PATH')
            ty_group_path.ty_id = ty_detail.id
            try:
                self.session.add(ty_group_path)
                self.session.commit()
                # 获取 ty_group_path 的 id
                if self.dict_data['LIST_TY_REALDATA']:
                    list_ty_realdata: List[TyphoonForecastRealDataModel] = self.dict_data.get('LIST_TY_REALDATA')
                    for ty_realdata in list_ty_realdata:
                        ty_realdata.gp_id = ty_group_path.id
                        ty_realdata.ty_id = ty_detail.id
                        self.session.add(ty_realdata)
                    self.session.commit()
                    is_stored = True
            except Exception as ex:
                print(f'{ex.args}')
        return is_stored

    @property
    def relative_path(self) -> str:
        """
            存储 group 集合预报路径的的相对路径
        @return:
        """
        # 台风名称前缀
        ty_prefix = 'TY'
        # TY2022_2020042710
        ty_full_name = f'{ty_prefix}{self.ty_code}_{self.timestmap}'
        return ty_full_name

    @property
    def save_dir_path(self) -> str:
        """

        :param kwargs:
        :return:
        """
        # todo:[*] 21-07-20 此处暂时使用明杰的目录结构，修改了之前的目录结构
        # eg: ROOT_PATH\pathfiles\TYTD04_2021071908
        # 之前为 : ROOT_PATH\ ty_timestamp \group
        # final_path_str = str(pathlib.Path(self.root_path) / self.relative_path / 'GROUP')
        # TODO:[-] 21-09-03 注意存储的路径为:
        # E:\05DATA\01nginx_data\nmefc_download\TY_GROUP_RESULT\TY2112_1630655410\pathfiles
        final_path_str = str(pathlib.Path(self.root_path) / 'pathfiles' / self.relative_path)
        return final_path_str

    @property
    def name_split(self) -> List[str]:
        """
            将 self.file_name 按照 split_stamp 切分为数组
        @return:
        """
        # ['TY1822', '2020052818', 'r6', 'p05']
        list_split: List[str] = []
        split_stamp: str = '_'  # 分隔符
        if self.file_name:
            list_split = self.file_name.split(split_stamp)
        return list_split

    @property
    def ty_code(self) -> str:
        """
            获取 台风 code
        @return:
        """

        code: str = None
        if len(self.name_split) > 0:
            # TY1822 -> 1822
            code = self.name_split[0][2:]
        return code

    @property
    def ty_timestmap(self) -> str:
        """
            获取 台风的时间戳
        @return:
        """
        ts_str: str = None
        if len(self.name_split) > 1:
            ts_str = self.name_split[1]
        return ts_str

    @property
    def ty_bp_stamp(self) -> str:
        """
            获取 台风 气压 标识
            eg: TY1822_2020042710_l5_p05 -> p05
        @return:
        """
        temp_stamp: str = None
        if len(self.name_split) > 3:
            if len(self.name_split) > 4:
                temp_stamp: str = f'{self.name_split[3]}_{self.name_split[4]}'
            else:
                temp_stamp: str = self.name_split[3]
        return temp_stamp

    @property
    def ty_bp_isIncrease(self) -> bool:
        """
            获取 气压的 是否为增量
            eg: TY1822_2020042710_l5_p05 -> true

        @return:
        """
        stamp: str = '_'
        if self.ty_bp_stamp.find(stamp) >= 0:
            return False
        else:
            return True

    @property
    def ty_bp_val(self) -> int:
        """
            获取 group file 的 偏移气压值
            eg: TY1822_2020042710_l5_p05 -> 05
        @return:
        """
        return int(self.ty_bp_stamp[-2:])

    @property
    def ty_path_stamp(self) -> str:
        """
            获取 台风路径 标志
            eg: TY1822_2020042710_l5_p05 -> l5
        @return:
        """
        path_type: str = None
        if len(self.name_split) > 1:
            path_type = self.name_split[2]
        return path_type

    @property
    def ty_path_type(self) -> str:
        return self.ty_path_stamp[:1].lower()

    @property
    def ty_path_marking(self) -> int:
        return int(self.ty_path_stamp[1:])

    def get_match_files(self, dir_path: str = None) -> List[str]:
        """
            获取指定路径下 符合正则表达式的 files_list
        @param dir_path:
        @return:
        """
        target_path = self.save_dir_path
        list_files: List[str] = []
        if dir_path:
            target_path = dir_path
        for file_name in os.listdir(target_path):
            pattern = re.compile(self.re)
            if re.match(pattern, file_name):
                list_files.append(file_name)
        return list_files

    def get_ty_num(self) -> str:
        """
            获取台风的编号
        @return:
        """
        pass

    def read_forecast_data(self, **kwargs):
        """
            读取 预报 数据
        @param kwargs:
        @return:
        """
        df_temp: pd.DataFrame = self.dict_data.get("DF")
        ty_detail = kwargs.get('ty_detail')
        # TY1822_2020042710_c0_p_05
        file_name: str = kwargs.get('file_name')
        # ['TYTD04', '2021071908', 'c0', 'p00']
        # ['TY2022', '2021010416', 'c0', 'p00']
        file_splits: List[str] = file_name.split('_')
        # TODO:[-] 21-04-20 BUG: 此处会造成首次读取文件后 df 不会更新的bug
        # if df_temp is None:
        # eg:
        # /Users/liusihan/data/typhoon_data/TY2022_2020042710/TY1822_2020042710
        # 实际 full_path :
        # /Users/liusihan/data/typhoon_data/TY2022_2020042710/TY1822_2020052818/TY1822_2020052818_r6_p05
        # TODO:[*] 21-07-20 与实际存储路径不符
        # full_path : 'E:\\01data\\01docker-data\\05container-shared-data\\01docker-ty\\TYTD04_2021071908\\GROUP\\TYTD04_2021071908_c0_p00'
        # file_name : TYTD04_2021071908_c0_p00
        full_path = str(pathlib.Path(self.save_dir_path) / file_name)
        df_temp = self.init_forecast_data(group_path_file=full_path)
        list_ty_path_mid: List[GroupTyphoonPathMidModel] = []
        list_ty_path: List[TyphoonGroupPathModel] = []
        # 注意每个 集合预报路径 创建一个 ty_group_path model
        ty_path: TyphoonGroupPathModel = TyphoonGroupPathModel(ty_code=self.typhoon_code,
                                                               file_name=self.file_name,
                                                               relative_path=self.relative_path,
                                                               timestamp=self.ty_timestmap,
                                                               ty_path_type=self.ty_path_type,
                                                               ty_path_marking=self.ty_path_marking, bp=self.ty_bp_val,
                                                               is_bp_increase=self.ty_bp_isIncrease)
        list_ty_realdata: List[TyphoonForecastRealDataModel] = []
        # list_ty_path.append(ty_path)
        # 先判断 df 中的预报时间是否与写入的 dt_range 匹配
        if len(df_temp) > 3 and self.forecast_dt_range == len(df_temp.iloc[3:]):
            index_forecast_dt = 0
            for index in range(3, len(df_temp)):
                series_temp: pd.Series = df_temp.iloc[index]
                # ['091517', '119.2', '18.9', '940.0', '37.0']
                list_split: List[str] = series_temp.values[0].split(' ')
                # TODO:[-] 21-07-26 此处修改了之前的年份是写死的，现在改成由文件名获取
                # 从 file_name 中提取年份
                # TODO:[-] 21-07-30 注意此处有一个大坑 取年份需要通过台风编号获取，此处目前的办法是只能将 年份暂时写死
                # year_header
                # # ['TY2022', '2021010416', 'c0', 'p00']
                # year_str = file_splits[1][:4]
                # TY2022 -> 20
                year_str = YEAR_HEADER + file_splits[0][2:-2]
                # 注意此处的 forecast_dt 是 local 时间 需要 -> utc
                # step: str -> arrow,set local -> to utc -> to datetime
                forecast_dt: datetime = arrow.get(year_str + list_split[0], 'YYYYMMDDHH', tzinfo='local').to(
                    'utc').datetime
                coords: List[float] = [float(list_split[2]), float(list_split[1])]
                lat: float = float(list_split[2])
                lon: float = float(list_split[1])
                bp: float = float(list_split[3])
                radius: float = float(list_split[4])
                ty_path_mid: GroupTyphoonPathMidModel = GroupTyphoonPathMidModel(forecast_dt, coords, bp, radius)
                ty_realdata: TyphoonForecastRealDataModel = TyphoonForecastRealDataModel(forecast_dt=forecast_dt,
                                                                                         forecast_index=index_forecast_dt,
                                                                                         # coords=coords,
                                                                                         lat=lat, lon=lon,
                                                                                         bp=bp,
                                                                                         gale_radius=radius,
                                                                                         timestamp=self.ty_timestmap)
                index_forecast_dt = index_forecast_dt + 1
                list_ty_realdata.append(ty_realdata)

                # list_ty_path_mid.append(ty_path_mid)

        self.dict_data['TY_PATH'] = ty_path
        self.dict_data['LIST_TY_REALDATA'] = list_ty_realdata
        pass

    @property
    def verify(self) -> bool:
        """
            验证当前 df 是否正常
        @return:
        """
        is_ok: bool = False
        df_temp = self.dict_data.get("DF")
        if df_temp is not None:
            if len(df_temp) > 0:
                is_ok = True
        return is_ok

    @property
    def typhoon_code(self) -> str:
        """
            从 当前的 dataframe 中获取 台风 code
        @return:
        """
        code: str = UNLESS_CODE
        df_temp: pd.DataFrame = self.dict_data.get("DF")
        if self.verify:
            code = df_temp.iloc[0].values[0]
        return code

    @property
    def forecast_dt_range(self) -> int:
        """
            获取预报时间范围
        @return:
        """
        df_temp: pd.DataFrame = self.dict_data.get("DF")
        dt_range: int = UNLESS_RANGE
        if self.verify:
            dt_range = int(df_temp.iloc[2].values)
        return dt_range

    def init_forecast_data(self, **kwargs) -> pd.DataFrame:
        """
            获取 预报的 data
        @return:
        """
        data: pd.DataFrame = None
        full_path: str = kwargs.get('group_path_file', None)
        if full_path is not None:
            # TODO:[-] 21-04-15 此处加入判断若指定文件存在
            if pathlib.Path(full_path).is_file():
                with open(full_path, 'rb') as f:
                    data = pd.read_table(f, encoding='utf-8', header=None, infer_datetime_format=False)
                    # print('读取成功')
                    if data is not None:
                        self.dict_data['DF'] = data
        return data


class StationRealDataFile(ITyphoonPath):
    def __init__(self, root_path: str, file_name: str, timestmap_str: str, gp_id: int,
                 forecast_dt_start: datetime):
        super(StationRealDataFile, self).__init__(root_path, file_name, timestmap_str)
        # super().__init__(root_path, file_name, timestmap_str)
        self.list_forecast_data: List[GroupTyphoonPathMidModel] = []
        # 台风集合预报路径的正则
        self.re = '^Surge_[A-Z]+\d+_\d+_[a-z]{1}\d{1}_[a-z]{1}_?\d+'
        # self.ty_code = ty_code
        self.gp_id = gp_id
        self.forecast_dt_start = forecast_dt_start

    @property
    def ty_code(self) -> str:
        """
            获取 台风 code
            TODO:[*] 21-04-23 此处与 GroupTyPath 相同，可去掉
        @return:
        """
        code: str = None
        if len(self.name_split) > 0:
            # TY1822 -> 1822
            code = self.name_split[0][2:]
        return code

    @property
    def name_split(self) -> List[str]:
        """
            将 self.file_name 按照 split_stamp 切分为数组,注意去掉了后缀 .dat 后的文件名称
            去掉了 Surge ，保持与 GroupTyPath 相同的 name_split
            ['TY2022', '2021010416', 'c0', 'p', '05']
        @return:
        """
        # [['Surge', 'TY2022', '2021010416', 'c0', 'p', '05.dat']]
        # - >
        # ['Surge', 'TY2022', '2021010416', 'c0', 'p', '05']
        list_split: List[str] = []
        split_stamp: str = '_'  # 分隔符
        if self.file_name:
            full_name_remove_ext: str = self.file_name[:self.file_name.find('.')]  # 移除了后缀的文件名
            list_split = full_name_remove_ext.split(split_stamp)[1:]  # ['TY2022', '2021010416', 'c0', 'p', '05']
        return list_split

    @property
    def save_dir_path(self) -> str:
        """

        :param kwargs:
        :return:
        """
        # TODO:[-] 21-07-27 此处使用明杰的目录结构
        # final_path_str = str(pathlib.Path(self.root_path) / self.relative_path / 'STATION')
        final_path_str = str(pathlib.Path(self.root_path) / 'result' / self.relative_path)
        return final_path_str

    def read_forecast_data(self, **kwargs):
        # TODO:[*] 21-04-23 此处存在一个如何获取 tyGroupPathModel 的问题
        df_temp: pd.DataFrame = self.dict_data.get("DF")
        timestamp_str: str = kwargs.get('timestamp')
        ty_detail = kwargs.get('ty_detail')
        file_name: str = kwargs.get('file_name')
        full_path: str = str(pathlib.Path(self.save_dir_path) / file_name)
        forecast_area: ForecastAreaEnum = kwargs.get('forecast_area') if kwargs.get('forecast_area',
                                                                                    None) is not None else ForecastAreaEnum.SCS
        df_temp: pd.DataFrame = self.init_forecast_data(group_path_file=full_path)
        list_station_realdata: List[StationForecastRealDataModel] = []
        # 先判断 df 中的预报时间是否与写入的 dt_range 匹配
        if df_temp is not None:
            num_columns = df_temp.shape[0]  # 行数
            num_rows = df_temp.shape[1]  # 列数
            # TODO:[-] 22-01-18 加入了根据传入的参数获取对应海区的步骤
            current_dict: dict = get_area_dict_station(forecast_area)
            # 列与 common/common_dict -> DICT_STATION 的 key 对应
            for index_column in range(num_rows):
                # TODO:[-] 22-01-18: 注意此处修改为动态字典
                station_code: str = current_dict[index_column]
                series_column = df_temp[index_column]
                index_row = 0
                current_dt: datetime = self.forecast_dt_start
                delta = timedelta(hours=1)
                for val_row in series_column:
                    # forecast_start=
                    station_realdata = StationForecastRealDataModel(ty_code=self.ty_code, gp_id=self.gp_id,
                                                                    station_code=station_code, forecast_dt=current_dt,
                                                                    forecast_index=index_row, surge=val_row,
                                                                    timestamp=timestamp_str)
                    index_row = index_row + 1
                    current_dt = current_dt + delta
                    # 对当前时间进行 hours +1
                    list_station_realdata.append(station_realdata)
        self.dict_data['LIST_TY_REALDATA'] = list_station_realdata

    def init_forecast_data(self, **kwargs) -> pd.DataFrame:
        """
            获取 预报的 data
        @return:
        """
        data: pd.DataFrame = None
        full_path: str = kwargs.get('group_path_file', None)
        df: pd.DataFrame = None
        if full_path is not None:
            # TODO:[-] 21-04-15 此处加入判断若指定文件存在
            if pathlib.Path(full_path).is_file():
                df: pd.DataFrame = pd.read_csv(full_path, sep='\\s+', header=None)
                shape_df: {} = df.shape
                num_columns: int = shape_df[0]
                num_rows: int = shape_df[1]
                if df is not None:
                    self.dict_data['DF'] = df
        return df

    def to_store(self, ty_detail: TyphoonForecastDetailModel, **kwargs) -> bool:
        is_stored = False
        try:
            # 获取 ty_group_path 的 id
            if self.dict_data['LIST_TY_REALDATA']:
                list_ty_realdata: List[StationForecastRealDataModel] = self.dict_data.get('LIST_TY_REALDATA')
                for ty_realdata in list_ty_realdata:
                    # ty_realdata.gp_id = ty_group_path.id
                    ty_realdata.ty_id = ty_detail.id
                    self.session.add(ty_realdata)
                self.session.commit()
                is_stored = True
        except Exception as ex:
            # ERROR:
            # (MySQLdb._exceptions.IntegrityError) (1364, "Field 'lat' doesn't have a default value")
            # [SQL: INSERT INTO station_forecast_realdata (is_del, gmt_created, gmt_modified, ty_code, gp_id, station_code, forecast_dt, forecast_index, surge) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)]
            # [parameters: (0, datetime.datetime(2021, 4, 25, 9, 15, 39, 714482), datetime.datetime(2021, 4, 25, 9, 15, 39, 714482), '2022', 147, 'SHW', datetime.datetime(2020, 9, 15, 17, 0), 0, 0.0)]
            # (Background on this error at: http://sqlalche.me/e/13/gkpj)
            print(f'{ex.args}')

        return is_stored


class FieldSurgeDataInfo:
    """
        逐时潮位 ds info 类
        用来处理逐时 ds -> db
           foreach    -> tif
    """

    def __init__(self, file: FieldSurgeCoverageFile, dir_path: str):
        self.file: FieldSurgeCoverageFile = file
        self.dir_path = dir_path
        self.ds: xar.Dataset = None
        self.session = DbFactory().Session
        self.dict_data = {
            'coverage_file': None,
            'tif_files': []
        }

    @property
    def full_file_name(self) -> str:
        """
            文件全名称
            xxx.nc
        @return:
        """
        return self.file.file_name

    @property
    def file_name(self) -> str:
        """
            根据 self.file -> file_name -> 只获取 file_name 不包含 .nc
        @return:
        """
        file_name_str: str = self.full_file_name
        file_name_temp: str = file_name_str.split('.')[0]
        return file_name_temp

    def to_do(self, **kwargs):
        """
            处理逐时风暴增水场文件
        @return:
        """
        gmt_start: datetime = kwargs.get('gmt_start')
        self.ds = self.read_nc()
        # self._gen_dt_range(gmt_start)
        converted_file_name: str = self.to_converted_nc(gmt_start)
        if converted_file_name:
            self.enumerate_2_tif()
            self.to_store()
        pass

    def read_nc(self) -> xar.Dataset:
        # step:
        # 1- 获取实际路径
        # 2- 判断是否存在指定文件
        # 3- 文件存在则读取，并返回 xarray.Dataset
        ds: xar.Dataset = None
        full_path: str = str(pathlib.Path(self.dir_path) / self.file.file_name)
        if pathlib.Path(full_path).is_file():
            ds = xar.open_dataset(full_path, decode_times=False)
        return ds

    def _gen_dt_range(self, gmt_start: datetime, ds: xar.Dataset = None, hours=48):
        """
            根据 gmt_start -> hours 生成时间数组作为 Dataset 的纬度
        @param gmt_start:
        @param hours:
        @return:
        """
        # TODO:[*] 21-09-08 注意此处有可能实际的 ds 的时间维度并不是 48 此处修改为 根据 dataset.dim.times
        num_times: int = self.ds.dims.get('times')
        # TODO:[!] 21-09-08 注意此处需要将传入的 gmt_start 的时区去掉,切记切记!!不然会在 xarray .to_netcdf 时出错!!
        gmt_start = gmt_start.replace(tzinfo=None)
        np_dt_range = np.array([gmt_start + timedelta(hours=i) for i in range(num_times)])
        # test_gmt_start = datetime(2021, 9, 15, 0, 0)
        # num_times = 120
        # np_dt_range = np.array([test_gmt_start + timedelta(hours=i) for i in range(num_times)])
        ds_temp: xar.Dataset = None
        if ds is not None:
            ds.coords['times'] = np_dt_range
            ds_temp = ds
        else:
            self.ds.coords['times'] = np_dt_range
            ds_temp = self.ds
        return ds_temp

    def to_converted_nc(self, gmt_start: datetime) -> str:
        """
            将 ds 生成转换后的 nc文件
            若生成成功返回 true
        @return:
        """
        is_converted: bool = False
        new_file_name: str = None
        if self.full_file_name.find('.') >= 0:
            new_file_name = self.full_file_name.split('.')[0] + '_converted.' + self.full_file_name.split('.')[1]
            new_full_path: str = str(pathlib.Path(self.dir_path) / new_file_name)
            if self.ds:
                converted_ds: xar.Dataset = self.ds
                converted_ds = converted_ds.rename_vars({'latitude': 'y', 'longitude': 'x'})
                converted_ds = converted_ds.swap_dims({'lat': 'y', 'lon': 'x'})
                converted_ds.rio.set_spatial_dims("x", "y", inplace=True)
                converted_ds = converted_ds.rio.write_crs("epsg:4326", inplace=True)
                converted_ds['y'] = converted_ds['y'][::-1]

                # TODO:[*] error: 出现了时间转换的错误，暂时将 之前的调用 _gen_dt_range 放在此处
                # ValueError: unable to infer dtype on variable 'times'; xarray cannot serialize arbitrary Python objects
                converted_ds = self._gen_dt_range(gmt_start, converted_ds)
                converted_ds.to_netcdf(new_full_path)
                self.ds = converted_ds
                is_converted = True
                self.dict_data['converted_file'] = new_file_name
        return new_file_name

    def to_store(self):
        """
            将以上步骤持久化保存
            step:
                -1 保存 coverage_file un_converted
                -2 保存 coverage_file converted
                -3 批量保存 tifs
        @return:
        """
        try:
            converted_full_name = self.dict_data.get('converted_file')
            # step: 1 保存 coverage_file un_converted
            ty_coverage_info = CoverageInfoModel(ty_code=self.file.ty_code, timestamp=self.file.ty_timestamp,
                                                 root_path=ROOT_PATH, file_name=self.file.file_name_only,
                                                 relative_path=self.file.ty_timestamp,
                                                 coverage_type=LayerType.FIELDSURGECOVERAGE.value, file_ext='nc')
            # step: 2 保存 coverage_file converted
            ty_coverage_info_converted = CoverageInfoModel(ty_code=self.file.ty_code, timestamp=self.file.ty_timestamp,
                                                           root_path=ROOT_PATH, file_name=converted_full_name,
                                                           relative_path=self.file.ty_timestamp, is_source=False,
                                                           coverage_type=LayerType.FIELDSURGECOVERAGE.value,
                                                           file_ext='nc')
            self.session.add(ty_coverage_info)
            self.session.add(ty_coverage_info_converted)
            # step: 3 保存 geo_tif
            list_tif_files: List[TifFileMidModel] = self.dict_data.get('tif_files')
            # TODO:[-] 21-08-05 注意此处存储的时候存在一个bug，逐时的 file.ty_timestamp 不包含 TY2022_,需要手动加上
            field_relative_path: str = f'TY{self.file.ty_code}_{self.file.ty_timestamp}'
            for temp_tif_file in list_tif_files:
                tif_model = ForecastTifModel(ty_code=self.file.ty_code, timestamp=self.file.ty_timestamp,
                                             root_path=ROOT_PATH, file_name=temp_tif_file.file_name,
                                             relative_path=field_relative_path,
                                             forecast_dt=temp_tif_file.forecast_dt,
                                             file_ext=temp_tif_file.file_ext,
                                             coverage_type=LayerType.FIELDSURGETIF.value)
                self.session.add(tif_model)
            self.session.commit()

        except Exception as ex:
            print(f'{ex.args}')

            pass

    def enumerate_2_tif(self):
        """
            将 self.ds 遍历 -> .tif
        @return:
        """
        if self.ds:
            file_name_coverage: str = self.file_name
            # 遍历生成 tif
            for temp in self.ds['times']:
                dt_temp = pd.to_datetime(temp.values)
                dt_str = arrow.get(dt_temp).format('YYYYMMDDHHmm')
                print(dt_str)
                ds_xr_temp = self.ds.sel(times=pd.to_datetime(temp.values))
                p = pathlib.Path(self.dir_path)
                file_name = f'{file_name_coverage}_{dt_str}.tif'
                full_path = str(p / file_name)
                print(f'最后输出的目录为{full_path}')
                ds_xr_temp.rio.to_raster(full_path)
                temp_file_info = TifFileMidModel(temp.values, file_name, full_path)
                self.dict_data.get('tif_files').append(temp_file_info)
                # print('-------------')
        pass


class ProSurgeDataInfo:
    """
        潮位概率分布 ds info 类
        用来处理逐时 ds -> db
           foreach    -> tif
    """

    # dict_data = {
    #     'coverage_file': None,  # 注意存储的是文件名，非 full_path
    #     'tif_files': []
    # }

    def __init__(self, file: ProSurgeCoverageFile, dir_path: str):
        self.file: ProSurgeCoverageFile = file
        self.dir_path = dir_path
        self.ds: xar.Dataset = None
        self.session = DbFactory().Session
        self.dict_data = {
            'coverage_file': None,  # 注意存储的是文件名，非 full_path
            'tif_files': []
        }

    @property
    def full_file_name(self) -> str:
        """
            文件全名称
            xxx.nc
        @return:
        """
        return self.file.file_name

    @property
    def file_name(self) -> str:
        """
            根据 self.file -> file_name -> 只获取 file_name 不包含 .nc
        @return:
        """
        file_name_str: str = self.full_file_name
        file_name_temp: str = file_name_str.split('.')[0]
        return file_name_temp

    def to_do(self, **kwargs):
        if self.to_converted_nc(True):
            self.to_tif()
            self.to_store()
        pass

    def _read_nc(self) -> xar.Dataset:
        # step:
        # 1- 获取实际路径
        # 2- 判断是否存在指定文件
        # 3- 文件存在则读取，并返回 xarray.Dataset
        ds: xar.Dataset = None
        full_path: str = str(pathlib.Path(self.dir_path) / self.file.file_name)
        if pathlib.Path(full_path).is_file():
            ds = xar.open_dataset(full_path, decode_times=False)
        self.ds = ds

    def _to_stand(self) -> bool:
        """
            对当前的 ds 标准化
            若标准化失败返回 false | 成功返回 true
        @return:
        """
        is_standed: bool = False
        if self.ds is None:
            self._read_nc()
        temp_ds: xar.Dataset = self.ds
        try:
            temp_ds = temp_ds.rename_vars({'latitude': 'y', 'longitude': 'x'})
            temp_ds = temp_ds.swap_dims({'lat': 'y', 'lon': 'x'})
            temp_ds.rio.set_spatial_dims("x", "y", inplace=True)
            temp_ds = temp_ds.rio.write_crs("epsg:4326", inplace=True)
            temp_ds = temp_ds.reindex(y=temp_ds.y[::-1])
            self.ds = temp_ds
            is_standed = True
        except Exception as e:
            print(e.args)
        return is_standed

    def to_converted_nc(self, to_save: bool = True) -> bool:
        """
            将当前 ds_xr 标准化后存储为新的 dataset
        @param to_save: true 存储为新的 nc eg:xx_converted.nc
        @return:
        """
        if self.ds is None:
            self._read_nc()
        is_ok: bool = self._to_stand()
        if to_save and is_ok:
            new_file_name: str = self.file_name + '_converted.nc'
            new_full_path: str = str(pathlib.Path(self.dir_path) / new_file_name)
            self.ds.to_netcdf(new_full_path)
            # 注意 此处 converted_file 存储的是文件名
            self.dict_data['converted_file'] = new_file_name
        return is_ok

    def to_tif(self) -> bool:
        """

        @return:
        """
        is_ok: bool = False
        # TODO:[-] 21-08-09 由于 pro -> tif 只有一个 tif，所以每次需要将 tif_files 清空，不然会有重复出现的情况
        self.dict_data['tif_files'] = []
        try:
            file_name_coverage: str = self.file_name
            p = pathlib.Path(self.dir_path)
            file_name = f'{file_name_coverage}.tif'
            full_path = str(p / file_name)
            print(f'最后输出的目录为{full_path}')
            self.ds.rio.to_raster(full_path)
            temp_file_info = TifProFileMidModel(file_name, full_path)
            self.dict_data.get('tif_files').append(temp_file_info)
            is_ok = True
        except Exception as e:
            print(e.args)
        return is_ok

    def to_store(self):
        """
            step:
                -1 保存 source coverage file
                -2 保存 converted coverage file
                -3 保存 tif
        @return:
        """
        try:
            converted_full_name = self.dict_data.get('converted_file')
            # step: 1 保存 coverage_file un_converted
            ty_coverage_info = CoverageInfoModel(ty_code=self.file.ty_code, timestamp=self.file.ty_timestamp,
                                                 root_path=ROOT_PATH, file_name=self.file.file_name_only,
                                                 relative_path=self.file.ty_timestamp,
                                                 coverage_type=self.file.coverage_type.value,
                                                 file_ext='nc')
            # step: 2 保存 coverage_file converted
            # TODO:[*] 21-08-09 注意此处的 converted_full_name 是包含后缀的，需要去掉后缀
            converted_full_name_only = converted_full_name.split('.')[0]
            ty_coverage_info_converted = CoverageInfoModel(ty_code=self.file.ty_code, timestamp=self.file.ty_timestamp,
                                                           root_path=ROOT_PATH, file_name=converted_full_name_only,
                                                           relative_path=self.file.ty_timestamp, is_source=False,
                                                           coverage_type=self.file.coverage_type.value,
                                                           file_ext='nc')
            self.session.add(ty_coverage_info)
            self.session.add(ty_coverage_info_converted)
            # step: 3 保存 geo_tif
            list_tif_files: List[TifFileMidModel] = self.dict_data.get('tif_files')
            # TODO:[-] 21-08-05 注意此处存储的时候存在一个bug，逐时的 file.ty_timestamp 不包含 TY2022_,需要手动加上
            field_relative_path: str = f'TY{self.file.ty_code}_{self.file.ty_timestamp}'
            for temp_tif_file in list_tif_files:
                tif_model = ForecastProTifModel(ty_code=self.file.ty_code, timestamp=self.file.ty_timestamp,
                                                root_path=ROOT_PATH, file_name=temp_tif_file.file_name,
                                                relative_path=field_relative_path,
                                                file_ext=temp_tif_file.file_ext,
                                                coverage_type=self.file.coverage_type.value, pro=self.file.surge_val)
                self.session.add(tif_model)
            self.session.commit()

        except Exception as ex:
            print(f'{ex.args}')

            pass


class MaxSurgeDataInfo:
    """
        + 21-11-16 最大增水场 ds info 类
        处理: ds -> db
             ds -> tif
    """

    def __init__(self, file: MaxSurgeCoverageFile, dir_path: str):
        self.file: MaxSurgeCoverageFile = file
        self.dir_path = dir_path
        self.ds: xar.Dataset = None
        self.session = DbFactory().Session
        self.dict_data = {
            'coverage_file': None,  # 注意存储的是文件名，非 full_path
            'tif_files': []
        }

    @property
    def full_file_name(self) -> str:
        """
            文件全名称
            xxx.nc
        @return:
        """
        return self.file.file_name

    @property
    def file_name(self) -> str:
        """
            根据 self.file -> file_name -> 只获取 file_name 不包含 .nc
        @return:
        """
        file_name_str: str = self.full_file_name
        file_name_temp: str = file_name_str.split('.')[0]
        return file_name_temp

    def to_do(self, **kwargs):
        log_in.info(f'准备对{str(pathlib.Path(self.dir_path) / self.file.file_name)}convert处理')
        if self.to_converted_nc(True):
            self.to_tif()
            self.to_store()
        pass

    def _read_nc(self) -> xar.Dataset:
        # step:
        # 1- 获取实际路径
        # 2- 判断是否存在指定文件
        # 3- 文件存在则读取，并返回 xarray.Dataset
        ds: xar.Dataset = None
        full_path: str = str(pathlib.Path(self.dir_path) / self.file.file_name)
        if pathlib.Path(full_path).is_file():
            ds = xar.open_dataset(full_path, decode_times=False)
        self.ds = ds

    def _to_stand(self) -> bool:
        """
            对当前的 ds 标准化
            若标准化失败返回 false | 成功返回 true
        @return:
        """
        is_standed: bool = False
        if self.ds is None:
            self._read_nc()
        temp_ds: xar.Dataset = self.ds
        try:
            temp_ds = temp_ds.rename_vars({'latitude': 'y', 'longitude': 'x'})
            temp_ds = temp_ds.swap_dims({'lat': 'y', 'lon': 'x'})
            temp_ds.rio.set_spatial_dims("x", "y", inplace=True)
            temp_ds = temp_ds.rio.write_crs("epsg:4326", inplace=True)
            # TODO:[-] 此处做如下修改，不使用 reindex
            # temp_ds = temp_ds.reindex(y=temp_ds.y[::-1])
            temp_ds['y'] = temp_ds['y'][::-1]
            self.ds = temp_ds
            is_standed = True
        except Exception as e:
            print(e.args)
        return is_standed

    def to_converted_nc(self, to_save: bool = True) -> bool:
        """
            将当前 ds_xr 标准化后存储为新的 dataset
        @param to_save: true 存储为新的 nc eg:xx_converted.nc
        @return:
        """
        if self.ds is None:
            self._read_nc()
        is_ok: bool = self._to_stand()
        if to_save and is_ok:
            log_in.info(f'{self.file_name}满足convert条件')
            new_file_name: str = self.file_name + '_converted.nc'
            new_full_path: str = str(pathlib.Path(self.dir_path) / new_file_name)
            log_in.info(f'{self.file_name}convertting...')
            self.ds.to_netcdf(new_full_path)
            log_in.info(f'{self.file_name}converted!')
            # 注意 此处 converted_file 存储的是文件名
            self.dict_data['converted_file'] = new_file_name
        return is_ok

    def to_tif(self) -> bool:
        """

        @return:
        """
        is_ok: bool = False
        # TODO:[-] 21-08-09 由于 max -> tif 只有一个 tif，所以每次需要将 tif_files 清空，不然会有重复出现的情况
        self.dict_data['tif_files'] = []
        try:
            file_name_coverage: str = self.file_name
            p = pathlib.Path(self.dir_path)
            file_name = f'{file_name_coverage}.tif'
            full_path = str(p / file_name)
            print(f'最后输出的目录为{full_path}')
            self.ds.rio.to_raster(full_path)
            temp_file_info = TifProFileMidModel(file_name, full_path)
            self.dict_data.get('tif_files').append(temp_file_info)
            is_ok = True
        except Exception as e:
            print(e.args)
        return is_ok

    def to_store(self):
        """
            step:
                -1 保存 source coverage file
                -2 保存 converted coverage file
                -3 保存 tif
        @return:
        """
        try:
            converted_full_name = self.dict_data.get('converted_file')
            # step: 1 保存 coverage_file un_converted
            ty_coverage_info = CoverageInfoModel(ty_code=self.file.ty_code, timestamp=self.file.ty_timestamp,
                                                 root_path=ROOT_PATH, file_name=self.file.file_name_only,
                                                 relative_path=self.file.ty_timestamp,
                                                 coverage_type=self.file.coverage_type.value,
                                                 file_ext='nc')
            # step: 2 保存 coverage_file converted
            # TODO:[*] 21-08-09 注意此处的 converted_full_name 是包含后缀的，需要去掉后缀
            converted_full_name_only = converted_full_name.split('.')[0]
            ty_coverage_info_converted = CoverageInfoModel(ty_code=self.file.ty_code, timestamp=self.file.ty_timestamp,
                                                           root_path=ROOT_PATH, file_name=converted_full_name_only,
                                                           relative_path=self.file.ty_timestamp, is_source=False,
                                                           coverage_type=self.file.coverage_type.value,
                                                           file_ext='nc')
            self.session.add(ty_coverage_info)
            self.session.add(ty_coverage_info_converted)
            # step: 3 保存 geo_tif
            list_tif_files: List[TifFileMidModel] = self.dict_data.get('tif_files')
            # TODO:[-] 21-08-05 注意此处存储的时候存在一个bug，逐时的 file.ty_timestamp 不包含 TY2022_,需要手动加上
            field_relative_path: str = f'TY{self.file.ty_code}_{self.file.ty_timestamp}'
            for temp_tif_file in list_tif_files:
                tif_model = ForecastTifModel(ty_code=self.file.ty_code, timestamp=self.file.ty_timestamp,
                                             root_path=ROOT_PATH, file_name=temp_tif_file.file_name,
                                             relative_path=field_relative_path,
                                             file_ext=temp_tif_file.file_ext,
                                             coverage_type=LayerType.MAXSURGETIF.value)
                self.session.add(tif_model)
            self.session.commit()

        except Exception as ex:
            print(f'{ex.args}')

            pass
