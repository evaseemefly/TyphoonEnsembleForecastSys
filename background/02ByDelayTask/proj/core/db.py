from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
#
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, text
from sqlalchemy.dialects.mysql import DATETIME, INTEGER, TINYINT, VARCHAR
from sqlalchemy import ForeignKey, Sequence, MetaData, Table
#
from datetime import datetime
from conf.settings import DATABASES


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
        self.port = db_options.get('POST')
        self.db_name = db_name if db_name else db_options.get('NAME')
        self.user = user if user else db_options.get('USER')
        self.password = pwd if pwd else db_options.get('PASSWORD')
        # self.engine = create_engine("mysql+pymysql://root:admin123@localhost/searchrescue", encoding='utf-8', echo=True)
        # TODO:[-] 21-09-29 新加入的 每次使用 session 之前进行简单的查询检查，判断 session是否过期
        # 参考文章: https://www.cnblogs.com/lesliexong/p/8654615.html
        # self.engine = create_engine(
        #     f"mysql+{self.engine_str}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}",
        #     encoding='utf-8', echo=True, pool_pre_ping=True)
        self.engine = create_engine(
            f"mysql+{self.engine_str}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}",
            encoding='utf-8', pool_pre_ping=True)
        self._session_def = sessionmaker(bind=self.engine)

    @property
    def Session(self) -> sessionmaker:
        if self._session_def is None:
            self._session_def = sessionmaker(bind=self.engine)
        return self._session_def()


def check_exist_table(tab_name: str) -> (bool, str):
    """
        - 22-05-24 判断指定 table 是否存在
    @param tab_name:
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


def create_station_surge_realdata_split_tab(ty_code: str,
                                            tab_base_name: str = 'station_forecast_realdata') -> str:
    """
        创建 海洋站潮位数据的分表
        eg:
            station_forecast_realdata_2107 | station_forecast_realdata_{ty_code}
    @param ty_code: 台风编号
    @param tab_base_name:表头基础字段(头部)
    @return:
    """
    tab_name: str = f'{tab_base_name}_{ty_code}'
    # 注意此处需要先判断是否已经存在指定的 tb
    # 方式1: 执行sql语句创建 tb —— 不使用此种方式
    sql_str: str = f""""
    create table {tab_name}
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
    return tab_name


def get_station_surge_dao(ty_code: str, tab_base_name: str = 'station_forecast_realdata') -> {}:
    """
        获取对应台风的动态表的映射dao实体
    @param ty_code:
    @param tab_base_name:
    @return:
    """
    db_name: str = 'typhoon_forecast_db_new'
    tab_name: str = f'station_forecast_realdata_{ty_code}'
    auto_base = automap_base()
    db_factory = DbFactory()
    engine = db_factory.engine
    auto_base.prepare(engine, reflect=True)
    StationSurgeDao = getattr(auto_base.classes, tab_name)
    return StationSurgeDao


def insert_station_surge_realdata_split_tab(ty_code: str, tab_base_name: str = 'station_forecast_realdata') -> str:
    tab_name: str = f'{tab_base_name}_{ty_code}'
    auto_base = automap_base()
    db_factory = DbFactory()
    engine = db_factory.engine
    auto_base.prepare(engine, reflect=True)
    StationSurgeDao = getattr(auto_base.classes, tab_name)
    pass
