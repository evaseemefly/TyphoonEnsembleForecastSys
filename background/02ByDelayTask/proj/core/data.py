#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/13 16:50
# @Author  : evaseemefly
# @Desc    : 用来放置 各类处理 data 的实现类
# @Site    :
# @File    : data.py
# @Software: PyCharm
from abc import ABCMeta, abstractclassmethod, abstractmethod, ABC
import pathlib
from typing import List
from model.mid_models import GroupTyphoonPathMidModel


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
    def __init__(self, root_path: str, ty_code: str, timestmap_str: str):
        self.root_path = root_path
        self.ty_code = ty_code
        self.timestmap = timestmap_str
        self.list_forecast_data: List[GroupTyphoonPathMidModel] = []

    def to_store(self, **kwargs) -> bool:
        pass

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
