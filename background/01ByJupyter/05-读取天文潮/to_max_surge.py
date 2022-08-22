#
import os
import pandas as pd
import numpy as np
import pathlib
import datetime
import arrow
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, text
from sqlalchemy.dialects.mysql import DATETIME, INTEGER, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Sequence, MetaData, Table
from sqlalchemy.orm import relationship, sessionmaker
# from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from enum import Enum, unique
from _PRIVACY import DB
from common import DICT_STATION


@unique
class PATTERNENMU(Enum):
    HOME = 1
    COMPANY = 2


PATTERN = PATTERNENMU.HOME

DB_PWD = DB.get('DB_PWD')

DATABASES = {
    'default': {
        'ENGINE': 'mysqldb',  # 数据库引擎
        'NAME': 'typhoon_forecast_db',  # 数据库名
        'USER': 'root',  # 账号
        'PASSWORD': DB_PWD if PATTERN == PATTERNENMU.COMPANY else '123456',
        'HOST': '127.0.0.1',  # HOST
        # 'HOST': '128.5.10.21',  # HOST
        'POST': 3306,  # 端口
        # 'PORT': 3308,  # TODO:[-] 21-10-11 端口暂时改为 3308
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
        },
    }
}


class DbFactory:
    """
        数据库工厂
    """

    def __init__(self, db_mapping: str = 'default', engine_str: str = None, host: str = None, db_name: str = None,
                 user: str = None,
                 pwd: str = None):
        db_options = DATABASES.get(db_mapping)
        self.engine_str = engine_str if engine_str else db_options.get('ENGINE')
        self.host = host if host else db_options.get('HOST')
        self.db_name = db_name if db_name else db_options.get('NAME')
        self.user = user if user else db_options.get('USER')
        self.password = pwd if pwd else db_options.get('PASSWORD')
        # self.engine = create_engine("mysql+pymysql://root:admin123@localhost/searchrescue", encoding='utf-8', echo=True)
        self.engine = create_engine(
            f"mysql+{self.engine_str}://{self.user}:{self.password}@{self.host}/{self.db_name}",
            encoding='utf-8', echo=True)
        self._session_def = sessionmaker(bind=self.engine)

    @property
    def Session(self) -> sessionmaker:
        if self._session_def is None:
            self._session_def = sessionmaker(bind=self.engine)
        return self._session_def()


engine = DbFactory().engine

# 生成基类
BaseMeta = declarative_base()
md = MetaData(bind=engine)  # 引用MetaData
metadata = BaseMeta.metadata


class TideDataModel(BaseMeta):
    # (1364, "Field 'id' doesn't have a default value") 需要手动设置数据库中的 id 字段为自增字段
    id = Column(Integer, primary_key=True, autoincrement=True)
    station_code = Column(VARCHAR(200), nullable=False)
    forecast_dt = Column(DATETIME(fsp=2))
    surge = Column(Float, nullable=False)
    tide_type = Column(Integer)

    __tablename__ = 'tide_data_daily'


@unique
class TideTypeEnum(Enum):
    PRIMARY = 8001
    MINOR = 8002


def is_stand_surge_data(surge_str: str, forecast_dt_str: str) -> bool:
    isOk = False
    # 判断传入的数据是否为标准化的数据
    if str(surge_str) != '9999' and str(forecast_dt_str) != '9999':
        isOk = True
    return isOk


def surge_data_2_stand(surge: str, forecast_dt_str: str, year: str, daily_start_time_utc: arrow.Arrow) -> dict:
    surge_dict = {}
    # eg: hhmm
    forecast_dt_str_converted = str(forecast_dt_str).rjust(4, '0')
    time = arrow.get(forecast_dt_str_converted, 'hhmm')
    # surge_fullDt_str = f'{year}-01-01 {forecast_dt_str_converted}'
    # surge_utc_dt = arrow.get(surge_fullDt_str, 'YYYY-MM-DD hhmm').shift(hours=-8)
    surge_utc_dt = daily_start_time_utc.shift(hours=time.hour).shift(minutes=time.minute)
    surge_dict['surge'] = surge
    surge_dict['dt'] = surge_utc_dt.datetime
    return surge_dict


def to_insert_db(session: sessionmaker, data: pd.DataFrame, year: str, station_full_code: str, station_code: str):
    # STATION_CODE = 'AOJIANG'
    year_start_dt_str_local = f'{year}-01-01'
    year_start_dt_local = arrow.get(year_start_dt_str_local, 'YYYY-MM-DD')
    year_start_dt_utc: arrow.Arrow = year_start_dt_local.shift(hours=-8)
    index_days = 0
    for day in range(data.shape[0]):
        current_date = year_start_dt_utc.shift(days=index_days)
        index_days = index_days + 1
        index_hours = 0
        # day 行(对应日期的数据)
        day_series = data.iloc[day]
        # 获取至多两个高潮位+高潮时
        # step1: 获取第一个高潮
        # 高潮1
        max_surge_val_1: np.int64 = data.iloc[day][25]
        max_surge_valStr_1: str = str(max_surge_val_1)
        max_surge_dtStr_1: np.int64 = data.iloc[day][24]
        max_surge_dtStr_1: str = str(max_surge_dtStr_1)
        # max_surge_dtStr_1=str(max_surge_dtStr_1).rjust(4,'0')
        # max_surge_fullDtStr_1=f'2022-01-01 {max_surge_dtStr_1}'
        # max_surge_dt_utc=arrow.get(max_surge_fullDtStr_1,'YYYY-MM-DD hh:mm').shift(hours=-8)
        if is_stand_surge_data(max_surge_valStr_1, max_surge_dtStr_1):
            max_surge_1_dict: dict = surge_data_2_stand(max_surge_valStr_1, max_surge_dtStr_1, year, current_date)
            _max_surge_1_str: str = max_surge_1_dict.get('surge')
            max_surge_1 = float(_max_surge_1_str)
            max_surge_1_utc_dt: datetime = max_surge_1_dict.get('dt')
            _tide_data = TideDataModel(station_code=station_code, surge=max_surge_1, forecast_dt=max_surge_1_utc_dt,
                                       tide_type=TideTypeEnum.PRIMARY.value)
            session.add(_tide_data)
        # step2:获取第二个高潮
        # 需要判断 index 26,27 是否为 9999 若为 9999 则为缺省值
        max_surge_val_2 = data.iloc[day][27]
        max_surge_dtStr_2 = data.iloc[day][26]
        if is_stand_surge_data(max_surge_val_2, max_surge_dtStr_2):
            max_surge_2_dict: dict = surge_data_2_stand(max_surge_val_2, max_surge_dtStr_2, year, current_date)
            _max_surge_2_str: str = max_surge_2_dict.get('surge')
            max_surge_2: float = float(_max_surge_2_str)
            max_surge_2_utc_dt = max_surge_2_dict.get('dt')
            _tide_data_2 = TideDataModel(station_code=station_code, surge=max_surge_2, forecast_dt=max_surge_2_utc_dt,
                                         tide_type=TideTypeEnum.MINOR.value)
            session.add(_tide_data_2)

    session.commit()


def main():
    # 根据 DICT_STATION 录入全部的海洋站数据
    # TODO:[*] 22-08-15 注意东海和南海各有一个海门站
    # 目前解决南海 海门G
    DICT_STATION = {'RAOPING': 'RPG', 'HENGMEN': 'HGM', 'MAGE': 'MGE', 'TAISHAN': 'TSH', 'BEIJIN': 'BJN',
                    'LEIZHOU': 'LZH', }
    for val, key in DICT_STATION.items():
        file_name = f'{val}2022'
        # read_path = r'C:\Users\evase\OneDrive\同步文件夹\02项目及本子\10-台风集合预报路径系统\数据\2022_天文潮\format_tide_2022'
        read_path = r'./data'
        full_path = str(pathlib.Path(read_path) / file_name)
        if pathlib.Path(full_path).exists():
            YEAR = '2022'
            session = DbFactory().Session
            with open(full_path, 'rb') as f:
                data = pd.read_table(f, sep='\s+', encoding='unicode_escape', header=None, infer_datetime_format=False)
                print('读取成功')
                to_insert_db(session, data, YEAR, val, key)
            pass


if __name__ == '__main__':
    main()
