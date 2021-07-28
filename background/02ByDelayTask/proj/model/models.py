#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/14 14:40
# @Author  : evaseemefly
# @Desc    : 用来放置 各类处理 data 的实现类
# @Site    :
# @File    : models.py
# @Software: PyCharm

# sqlalchemy 相关引用
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, text
from sqlalchemy.dialects.mysql import DATETIME, INTEGER, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Sequence, MetaData, Table
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
# geoalchemy2 相关y
from geoalchemy2 import Geometry

# 项目配置
from conf.settings import DATABASES
from core.db import DbFactory

from common.const import DEFAULT_FK, UNLESS_INDEX, DEFAULT_CODE

engine = DbFactory().engine

# 生成基类
BaseMeta = declarative_base()
md = MetaData(bind=engine)  # 引用MetaData
metadata = BaseMeta.metadata


class IIdModel(BaseMeta):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


class IDel(BaseMeta):
    """
        软删除 抽象父类
    """
    __abstract__ = True
    is_del = Column(TINYINT(1), nullable=False, server_default=text("'0'"), default=0)


class IModel(BaseMeta):
    """
        model 抽象父类，主要包含 创建及修改时间
    """
    __abstract__ = True
    gmt_created = Column(DATETIME(fsp=6), default=datetime.utcnow())
    gmt_modified = Column(DATETIME(fsp=6), default=datetime.utcnow())


class ITimeStamp(BaseMeta):
    """
        + 21-07-26 时间戳抽象父类
    """
    __abstract__ = True
    timestamp = Column(VARCHAR(100), nullable=False)


class TyphoonForecastRealDataModel(IIdModel, IDel, IModel, ITimeStamp):
    """
        台风逐时预报信息
    """
    __tablename__ = 'typhoon_forecast_realdata'
    ty_id = Column(Integer, nullable=False)
    gp_id = Column(Integer, nullable=False)
    forecast_dt = Column(DATETIME(fsp=6))
    forecast_index = Column(Integer, nullable=False)
    # coords = Column(Geometry('POINT'))
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    bp = Column(Float, nullable=False)
    gale_radius = Column(Float, nullable=False)
    # timestamp = Column(VARCHAR(100), nullable=False)


class StationForecastRealDataModel(IIdModel, IDel, IModel,ITimeStamp):
    """
        台站逐时潮位信息
    """
    __tablename__ = 'station_forecast_realdata'
    ty_code = Column(VARCHAR(200), nullable=False)
    gp_id = Column(Integer, nullable=False)
    station_code = Column(VARCHAR(200), nullable=False)
    # lat = Column(Float, nullable=False)
    # lon = Column(Float, nullable=False)
    forecast_dt = Column(DATETIME(fsp=2))
    forecast_index = Column(Integer, nullable=False)
    surge = Column(Float, nullable=False)


class TyphoonForecastDetailModel(IDel, IIdModel, IModel, ITimeStamp):
    __tablename__ = 'typhoon_forecast_detailinfo'

    code = Column(VARCHAR(200), nullable=False)
    organ_code = Column(Integer, nullable=False)
    gmt_start = Column(DATETIME(fsp=6))
    gmt_end = Column(DATETIME(fsp=6))
    forecast_source = Column(Integer, nullable=False)
    is_forecast = Column(TINYINT(1), nullable=False, server_default=text("'0'"), default=0)


class TyphoonGroupPathModel(IDel, IIdModel, IModel):
    __tablename__ = 'typhoon_forecast_grouppath'

    ty_id = Column(Integer, nullable=False, default=DEFAULT_FK)
    ty_code = Column(VARCHAR(200), nullable=False)
    file_name = Column(VARCHAR(200), nullable=False)
    relative_path = Column(VARCHAR(500), nullable=False)
    area = Column(Integer, nullable=False, default=DEFAULT_FK)
    timestamp = Column(VARCHAR(100), nullable=False)
    ty_path_type = Column(VARCHAR(5), nullable=False, default=DEFAULT_CODE)
    ty_path_marking = Column(Integer, nullable=False)
    bp = Column(Float, nullable=False)
    is_bp_increase = Column(TINYINT(1), nullable=False, server_default=text("'0'"), default=0)  # 气压是否为增量
