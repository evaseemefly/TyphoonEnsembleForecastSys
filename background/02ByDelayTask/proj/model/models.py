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
# geoalchemy2 相关
from geoalchemy2 import Geometry

# 项目配置
from conf.settings import DATABASES

from common.const import DEFAULT_FK,UNLESS_INDEX

engine = create_engine(
    f"mysql+{DATABASES.get('ENGINE')}://{DATABASES.get('USER')}:{DATABASES.get('PASSWORD')}@{DATABASES.get('HOST')}/{DATABASES.get('NAME')}",
    encoding='utf-8', echo=True)

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
    gmt_create_time = Column(DATETIME(fsp=6))
    gmt_modify_time = Column(DATETIME(fsp=6))


class TyphoonForecastRealDataModel(IIdModel, IDel, IModel):
    """
        台风逐时预报信息
    """
    __tablename__ = 'typhoon_forecast_realdata'
    ty_id = Column(Integer, nullable=False)
    gp_id = Column(Integer, nullable=False)
    forecast_dt = Column(DATETIME(fsp=6))
    forecast_index = Column(Integer, nullable=False)
    coords = Column(Geometry('POINT'))
    bp = Column(Float, nullable=False)
    gale_radius = Column(Float, nullable=False)


class TyphoonForecastDetailModel(IDel, IIdModel, IModel):
    __tablename__ = 'typhoon_forecast_detailinfo'

    code = Column(VARCHAR(200), nullable=False)
    organ_code = Column(VARCHAR(200), nullable=False)
    gmt_start = Column(DATETIME(fsp=6))
    gmt_end = Column(DATETIME(fsp=6))
    forecast_source = Column(VARCHAR(200), nullable=False)
    is_forecast = Column(VARCHAR(200), nullable=False)


class TyphoonGroupPathModel(IDel, IIdModel, IModel):
    __tablename__ = 'typhoon_forecast_grouppath'

    ty_id = Column(Integer, nullable=False,default=DEFAULT_FK)
    ty_code = Column(VARCHAR(200), nullable=False)
    file_name = Column(VARCHAR(200), nullable=False)
    relative_path = Column(VARCHAR(500), nullable=False)
    area = Column(Integer, nullable=False,default=DEFAULT_FK)
    timestamp = Column(VARCHAR(100), nullable=False)
    path_type = Column(Integer, nullable=False,default=UNLESS_INDEX)
    marking = Column(VARCHAR(10), nullable=False)
    bp = Column(Float, nullable=False)
    is_bp_increase = Column(TINYINT(1), nullable=False, server_default=text("'0'"), default=0)  # 气压是否为增量