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
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
# geoalchemy2 相关y
# from geoalchemy2 import Geometry

# 项目配置
from conf.settings import DATABASES
from core.db import DbFactory

from common.const import DEFAULT_FK, UNLESS_INDEX, NONE_ID, DEFAULT_CODE, DEFAULT_PATH_TYPE, DEFAULT_PRO, UNLESS_RANGE

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
    gmt_created = Column(DATETIME(fsp=6), default=datetime.utcnow)
    gmt_modified = Column(DATETIME(fsp=6), default=datetime.utcnow)


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


class StationForecastRealDataModel(IIdModel, IDel, IModel, ITimeStamp):
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


class StationStatisticsModel(IIdModel, IDel, IModel, ITimeStamp):
    """
        台站逐时潮位信息
    """
    __tablename__ = 'station_quantile_realdata'
    ty_code = Column(VARCHAR(200), nullable=False)
    station_code = Column(VARCHAR(200), nullable=False)
    forecast_dt = Column(DATETIME(fsp=2))
    forecast_index = Column(Integer, nullable=False)
    quarter_val = Column(Float, nullable=False)
    three_quarters_val = Column(Float, nullable=False)
    median_val = Column(Float, nullable=False)


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


class ITyPathModel(BaseMeta):
    """
        所有 file 包含台风路径信息的 父类
        maxSurge_TY2022_2021010416_c0_p00.nc  -> c0
    """
    __abstract__ = True
    ty_path_type = Column(VARCHAR(5), nullable=False, default=DEFAULT_PATH_TYPE)
    ty_path_marking = Column(Integer, nullable=False, default=0)


class IBpModel(BaseMeta):
    """
        所有 file 包含 台风气压信息的 父类
        maxSurge_TY2022_2021010416_c0_p00.nc  -> p00
    """
    __abstract__ = True
    bp = Column(Float, nullable=False, default=0)
    is_bp_increase = Column(TINYINT(1), nullable=False, default=0)  # 气压是否为增量


class ISpliceModel(BaseMeta):
    """
        是否已经进行切片 的 coverage
        若 is_splice = False 则 splice_step 可以为 NULL
    """
    __abstract__ = True
    is_splice = Column(TINYINT(1), nullable=False, default=0)
    splice_step = Column(Integer, nullable=True)


class IIsSourceModel(BaseMeta):
    __abstract__ = True
    is_source = Column(TINYINT(1), nullable=False, default=1)


class IFileModel(BaseMeta):
    """
        所有 file 的抽象父类 model
    """
    __abstract__ = True

    root_path = Column(VARCHAR(500), nullable=False)
    file_name = Column(VARCHAR(200), nullable=False)
    relative_path = Column(VARCHAR(500), nullable=False)
    file_size = Column(Float, nullable=False)
    file_ext = Column(VARCHAR(10), nullable=False)


class CoverageInfoModel(IDel, IIdModel, IModel, ITyPathModel, IBpModel, ISpliceModel, IIsSourceModel, IFileModel):
    __tablename__ = 'geo_coverageinfo'
    forecast_area = Column(Integer, nullable=False, default=0)
    coverage_type = Column(Integer, nullable=False, default=0)
    ty_code = Column(VARCHAR(100), nullable=False)
    timestamp = Column(VARCHAR(100), nullable=False)
    surge_max = Column(Float, nullable=False, default=UNLESS_RANGE)
    surge_min = Column(Float, nullable=False, default=UNLESS_RANGE)

class ForecastTifModel(IDel, IIdModel, IModel, ITyPathModel, IBpModel, ISpliceModel, IFileModel):
    __tablename__ = 'geo_forecast_tif'
    coverage_type = Column(Integer, nullable=False, default=0)
    ty_code = Column(VARCHAR(100), nullable=False)
    timestamp = Column(VARCHAR(100), nullable=False)
    forecast_dt = Column(DATETIME(fsp=6), default=datetime.utcnow(), nullable=True)
class ForecastProTifModel(IDel, IIdModel, IModel, ITyPathModel, ISpliceModel, IFileModel):
    __tablename__ = 'geo_forecast_pro_tif'
    coverage_type = Column(Integer, nullable=False, default=0)
    ty_code = Column(VARCHAR(100), nullable=False)
    timestamp = Column(VARCHAR(100), nullable=False)
    pro = Column(Float, nullable=False, default=DEFAULT_PRO)
class CaseStatus(IDel, IIdModel, IModel):
    """
        + 21-09-01 创建 case 的状态表
    """
    __tablename__ = 'task_casestatus'
    celery_id = Column(Integer, nullable=False, default=0)
    case_state = Column(Integer, nullable=False, default=0)
    case_rate = Column(Integer, nullable=False, default=0)
    is_lock = Column(TINYINT(1), nullable=False, default=1)
class RelaTyTaskModel(IIdModel):
    """
        + 21-09-14  typhoon 与 task 的关联表
    """
    __tablename__ = 'rela_ty_task'
    ty_id = Column(Integer, nullable=False, default=NONE_ID)
    celery_id = Column(Integer, nullable=False, default=NONE_ID)