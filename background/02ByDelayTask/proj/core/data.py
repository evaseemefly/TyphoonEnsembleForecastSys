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
from datetime import datetime
import arrow
from typing import List
from model.mid_models import GroupTyphoonPathMidModel
from common.const import UNLESS_CODE, UNLESS_RANGE
from conf.settings import TEST_ENV_SETTINGS

# root 的根目录
ROOT_PATH = TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR')


def get_match_files(re_str: str, dir_path: str = None) -> List[str]:
    """
        获取指定路径下 符合正则表达式的 files_list
    @param dir_path: 注意 dir_path 应该是 ROOT_PATH/台风code_timestamp/
    @return:
    """
    list_files: List[str] = []
    if dir_path:
        target_path = dir_path
        for file_name in os.listdir(target_path):
            pattern = re.compile(re_str)
            if re.match(pattern, file_name):
                list_files.append(file_name)
    return list_files


def to_ty_group(list_files: List[str], **kwargs):
    for file_temp in list_files:
        # eg:  TY1822_2020042710_l5_p05
        # eg2: TY1822_2020042710_c0_p_10
        file_name: str = pathlib.Path(file_temp).name
        name_split: List[str] = file_name.split('_')
        ty_code_stamp: str = name_split[0]  # TY1822
        ts_str: str = name_split[1]  # 2020042710
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
            ty_group = GroupTyphoonPath(ROOT_PATH, ty_code, ts_str)
            ty_group.read_forecast_data(file_name=file_name)
            ty_group.to_store()

        pass


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


class GroupTyphoonPath(IBaseOpt):
    dict_data = {
        'DF': None
    }

    def __init__(self, root_path: str, ty_code: str, file_name: str, timestmap_str: str):
        self.root_path = root_path
        self.ty_code = ty_code
        self.timestmap = timestmap_str
        self.file_name = file_name  # eg: TY1822_2020042710_l5_p05
        self.list_forecast_data: List[GroupTyphoonPathMidModel] = []
        # 台风集合预报路径的正则
        self.re = '^[A-Z]+\d+_\d+_[a-z]{1}\d{1}_[a-z]{1}_?\d+'

    def to_store(self, **kwargs) -> bool:
        """
            主要是将与 台风集合预报路径 相关的逻辑 to -> db
            GroupTYphoonPathModel + ForecastTyphoonDataModel
        @param kwargs:
        @return:
        """

        return False

    @property
    def save_dir_path(self, **kwargs) -> str:
        """

        :param kwargs:
        :return:
        """
        # 台风名称前缀
        ty_prefix = 'TY'
        # TY2022_2020042710
        ty_full_name = f'{ty_prefix}{self.ty_code}_{self.timestmap}'
        final_path_str = str(pathlib.Path(self.root_path) / ty_full_name)
        return final_path_str

    @property
    def name_split(self) -> List[str]:
        """
            将 self.file_name 按照 split_stamp 切分为数组
        @return:
        """
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
            code = self.name_split[0]
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
    def ty_bpStamp(self) -> str:
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
    def ty_path_type(self) -> str:
        """
            获取 台风路径 标志
            eg: TY1822_2020042710_l5_p05 -> l5
        @return:
        """
        path_type: str = None
        if len(self.name_split) > 1:
            path_type = self.name_split[2]
        return path_type

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
        # TY1822_2020042710_c0_p_05
        file_name: str = kwargs.get('file_name')
        if df_temp is None:
            full_path = str(pathlib.Path(self.save_dir_path) / file_name)
            df_temp = self.init_forecast_data(group_path_file=full_path)
        list_ty_path_mid: List[GroupTyphoonPathMidModel] = []
        # 先判断 df 中的预报时间是否与写入的 dt_range 匹配
        if len(df_temp) > 3 and self.forecast_dt_range == len(df_temp.iloc[3:]):
            for index in range(3, len(df_temp)):
                series_temp: pd.Series = df_temp.iloc[index]
                # ['091517', '119.2', '18.9', '940.0', '37.0']
                list_split: List[str] = series_temp.values[0].split(' ')
                year_str = '2020'
                forecast_dt: datetime = arrow.get(year_str + list_split[0], 'YYYYMMDDHH').datetime
                coords: List[float] = [float(list_split[2]), float(list_split[1])]
                bp: float = float(list_split[3])
                radius: float = float(list_split[4])
                ty_path_mid: GroupTyphoonPathMidModel = GroupTyphoonPathMidModel(forecast_dt, coords, bp, radius)
                list_ty_path_mid.append(ty_path_mid)
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
            with open(full_path, 'rb') as f:
                data = pd.read_table(f, encoding='utf-8', header=None, infer_datetime_format=False)
                print('读取成功')
                if data is not None:
                    self.dict_data['DF'] = data
        return data
