from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, text
from sqlalchemy.dialects.mysql import DATETIME, INTEGER, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Sequence, MetaData, Table
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

DATABASES = {
    'default': {
        'ENGINE': 'mysqldb',  # 数据库引擎
        'NAME': 'typhoon_forecast_db',  # 数据库名
        # by casablanca
        # mac
        'USER': 'root',  # 账号
        # 7530,mac
        # 'PASSWORD': 'admin123',
        # 5820,p52s,p500,razer
        'PASSWORD': '123456',
        # by cwb
        # 'USER': 'root',  # 账号
        # 'PASSWORD': '123456',
        # 'HOST': '127.0.0.1',  # HOST
        'HOST': 'host.docker.internal',  # docker访问宿主机的mysql服务
        'POST': 3306,  # 端口
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
        self.engine_str = engine_str if engine_str else db_options.get(
            'ENGINE')
        self.host = host if host else db_options.get('HOST')
        self.db_name = db_name if db_name else db_options.get('NAME')
        self.user = user if user else db_options.get('USER')
        self.password = pwd if pwd else db_options.get('PASSWORD')
        # self.engine = create_engine("mysql+pymysql://root:admin123@localhost/searchrescue", encoding='utf-8', echo=True)
        self.engine = create_engine(
            f"mysql+{self.engine_str}://{self.user}:{self.password}@{self.host}/{self.db_name}",
            encoding='utf-8', echo=False)
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


class IIdModel(BaseMeta):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


class IDel(BaseMeta):
    """
        软删除 抽象父类
    """
    __abstract__ = True
    is_del = Column(TINYINT(1), nullable=False,
                    server_default=text("'0'"), default=0)


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
    max_val = Column(Float, nullable=False)
    min_val = Column(Float, nullable=False)


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


session = DbFactory().Session


def get_target_dt_surge_quantile(ty_code: str, ty_timestamp: str, station_code: str, list_forecast_dt,
                                 forecast_index: int = 0, quantile: float = 1 / 2):
    """[summary]
       找到指定的百分位数
    Args:
        ty_code (str): [description]
        ty_timestamp (str): [description]
        station_code (str): [description]
        forecast_index (int, optional): [description]. Defaults to 0.
        quantile (float, optional): [description]. Defaults to 1/2.

    Returns:
        [type]: [description]
    """
    query = session.query(StationForecastRealDataModel).filter(StationForecastRealDataModel.ty_code == ty_code,
                                                               StationForecastRealDataModel.timestamp == ty_timestamp,
                                                               StationForecastRealDataModel.station_code == station_code,
                                                               StationForecastRealDataModel.forecast_dt ==
                                                               list_forecast_dt[forecast_index])
    count = len(query.all())
    # 找到百分位数位置
    index_quantile: int = int(count * quantile)
    if index_quantile == count:
        index_quantile = -1
    # 对于 query先根据 surge进行排序，再取数
    val_quantile: float = query.order_by(StationForecastRealDataModel.surge)[
        index_quantile].surge

    return val_quantile


def get_dist_station_code(ty_code: str, ty_timestamp: str):
    """[summary]
         获取海洋站的站代号列表
    Args:
        ty_code (str): [description]
        ty_timestamp (str): [description]
    """
    list_query = session.query(StationForecastRealDataModel).filter(StationForecastRealDataModel.ty_code == ty_code,
                                                                    StationForecastRealDataModel.timestamp == ty_timestamp).group_by(
        StationForecastRealDataModel.station_code).all()
    list_dist_station_code = [temp.station_code for temp in list_query]
    return list_dist_station_code


def get_dist_forecast_dt_list(ty_code: str, ty_timestamp: str, station_code: str):
    """[summary]
        获取指定台风的海洋站所有预报时刻
    Args:
        ty_code (str): [description]
        ty_timestamp (str): [description]
    """
    query_forecast_dt = session.query(StationForecastRealDataModel).filter(
        StationForecastRealDataModel.ty_code == ty_code,
        StationForecastRealDataModel.timestamp == ty_timestamp,
        StationForecastRealDataModel.station_code == station_code).group_by(
        StationForecastRealDataModel.forecast_dt).all()
    list_dist_forecast_dt = [temp.forecast_dt for temp in query_forecast_dt]
    return list_dist_forecast_dt


def main():
    station_code = 'SHW'
    ty_code = '2078'
    ty_timestamp = '1635231596'
    # list_dist_forecast_dt = get_dist_forecast_dt_list(ty_code, ty_timestamp, station_code)
    # get_target_dt_surge_quantile(ty_code, ty_timestamp, station_code, list_dist_forecast_dt)
    list_dist_forecast_dt = get_dist_forecast_dt_list(
        ty_code, ty_timestamp, station_code)
    list_dist_station_code = get_dist_station_code(ty_code, ty_timestamp)

    for temp_station_code in list_dist_station_code:
        for temp_forecast_index, temp_forecast_dt in enumerate(list_dist_forecast_dt):
            min = get_target_dt_surge_quantile(ty_code, ty_timestamp, temp_station_code,
                                               list_dist_forecast_dt,
                                               temp_forecast_index, 0)
            median_surge = get_target_dt_surge_quantile(ty_code, ty_timestamp, temp_station_code, list_dist_forecast_dt,
                                                        temp_forecast_index)
            quarter_surge = get_target_dt_surge_quantile(ty_code, ty_timestamp, temp_station_code,
                                                         list_dist_forecast_dt,
                                                         temp_forecast_index, 0.25)
            three_quarters_surge = get_target_dt_surge_quantile(ty_code, ty_timestamp, temp_station_code,
                                                                list_dist_forecast_dt,
                                                                temp_forecast_index, 0.75)
            max = get_target_dt_surge_quantile(ty_code, ty_timestamp, temp_station_code,
                                               list_dist_forecast_dt,
                                               temp_forecast_index, 1)
            temp_station_statistics_model: StationStatisticsModel = StationStatisticsModel(ty_code=ty_code,
                                                                                           timestamp=ty_timestamp,
                                                                                           station_code=temp_station_code,
                                                                                           forecast_dt=temp_forecast_dt,
                                                                                           forecast_index=temp_forecast_index,
                                                                                           quarter_val=quarter_surge,
                                                                                           three_quarters_val=three_quarters_surge,
                                                                                           median_val=median_surge,
                                                                                           max_val=max,
                                                                                           min_val=min)
            session.add(temp_station_statistics_model)
            pass
        session.commit()
    pass


if __name__ == '__main__':
    main()
