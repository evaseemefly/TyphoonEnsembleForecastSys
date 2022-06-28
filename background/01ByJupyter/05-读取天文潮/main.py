# 自动从 dict_stations 中遍历读取指定文件夹下的全部文件，并根据起止时间获取对应天文潮位并写入db
# 注意数据库中均为世界时
import os
import pandas as pd
import pathlib
import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, text
from sqlalchemy.dialects.mysql import DATETIME, INTEGER, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Sequence, MetaData, Table
from sqlalchemy.orm import relationship, sessionmaker
# from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASES = {
    'default': {
        'ENGINE': 'mysqldb',  # 数据库引擎
        'NAME': 'typhoon_forecast_db',  # 数据库名
        # 'NAME': 'typhoon_forecast_db_new',  # 数据库名
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
        # 'HOST': 'localhost',  # HOST
        # 'HOST': '127.0.0.1',  # HOST
        'HOST': '128.5.10.21',  # HOST
        # 'HOST': 'host.docker.internal',  # docker访问宿主机的mysql服务
        # 'POST': 3306,  # 端口
        'POST': 3308,  # TODO:[-] 21-10-11 端口暂时改为 3308
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
        },
    }
}

# TODO:[-] 22-06-22 注意 区域2 与 区域3 会有交集，若录入了区域3，需要剔除区域3中和区域2重合的station，否则会出现同一个station录入多次的错误
# 区域2中独有的 station
# {'BSH', 'WZS', 'QYU', 'CAO', 'DCH', 'SCS', 'DHI', 'SJM', 'GNS', 'SHA', 'SHS', 'BLN', 'MHA', 'BJA', 'JAT', 'KMN', 'AJS', 'BYT', 'RAS', 'SPU', 'ZPU', 'WSH', 'CHH', 'GTO'}
# 区域2 的字典
DICT_STATION = {
    # 芦潮港  10 711
    # 'LUCHAOG': 'LCG',
    # 大戢山  11 730
    # 'DAISHAN': 'DJS', # 没有大吉山
    # # 金山嘴  17 684
    # 'JINSHAN': 'JSZ',
    # # 滩浒    23 697
    # 3: 'TXU',       # TODO:[*] 22-06-21 没有滩浒的天文潮文件(2021)
    # 乍浦    26 667
    'ZHAPU': 'ZPU',
    # 澉浦    39 655
    # 5: 'GPU',   # TODO:[*] 22-06-21 没有澉浦的天文潮文件(2021) 注意 db 更新澉浦 GPU
    # 嵊山    17 768
    'SHENGSHAN': 'SHS',
    # 岱山    46 731
    'DAISHAN': 'DSH',
    # 定海    61 724
    'DINGHAI': 'DHI',
    # 镇海    61 704
    'ZHENHAIH': 'ZHI',
    # 沈家门  64 737
    'SHENJIAMEN': 'SJM',
    # 北仑    65 727
    'BEILUN': 'BLN',
    # 乌沙山  90 699
    'WUSS': 'WSH',
    # 石浦   106 719
    'SHIPU': 'SPU',
    # 健跳   117 699
    'JIANTIAO': 'JAT',
    # 海门Z  139 687
    'HAIMENZ': 'HMZ',  # TODO:[*] 22-06-21 天文潮位有两个，需对应
    # 大陈   153 714
    'DACHEN': 'DCH',
    # 坎门   175 679
    'KANMEN': 'KMN',
    # 温州S  181 645
    'WENZHOU2': 'WZS',
    # 瑞安S  197 641
    'RUIAN': 'RAS',
    # 鳌江S  206 638
    'AOJIANG': 'AJS',  # 没有鳌江S
    # 沙埕S  230 625
    'SHACHENG': 'SCS',  # 还有SHACHENGH
    # 秦屿   238 617
    'QINYU': 'QYU',
    # 三沙   246 614
    'SANSHA': 'SHA',
    # 北礵   258 621
    'BEISHUANG': 'BSH',
    # 城澳   263 584
    'CHENGAO': 'CAO',
    # 青屿   279 582
    'QINGYU': 'QGY',
    # 北茭   278 596
    'BJIAO': 'BJA',
    # 琯头   293 575
    'GUANTOU': 'GTO',
    # 梅花   299 581
    'MEIHUA': 'MHA',
    # 白岩潭 297 572
    'BAIYANT': 'BYT',
    # 平潭   332 590
    'PINGTANf': 'PTN',
    # 福清核 334 566
    'FUQINGHD': 'FQH',
    # 石城   344 562
    'SHICHENG': 'SHC',
    # 峰尾   353 538
    'FENGWEI': 'FHW',
    # 崇武H  368 536
    'CHONGWUH': 'CHW',
    # 晋江   382 520
    'JINJIANG': 'JJH',
    # 石井   381 507
    'SHIJING': 'SJH',
    # 厦门   393 484
    'XIAMEN': 'XMN',
    # 旧镇   421 463
    'JIUZHENG': 'JZH',
    # 古雷   432 459
    'GULEI': 'GUL',
    # 东山   436 452
    'DONGSHAN': 'DSH',
    # 赤石湾 442 434
    'CHISHIWAN': 'CSW',
    # 云澳   457 427
    'YUNAO': 'YAO',
    # 汕头S  460 405
    'SHANTOU': 'STO',
    # 海门G  470 397
    'HAIMENZ': 'HMN',  # 存在两个海门
    # 惠来   482 392
    'HUILAI': 'HLA',
    # 陆丰   491 366
    'LUFENG': 'LFG',
    # 遮浪   501 334
    'ZHELANG': 'ZHL',
    # 汕尾   495 321
    'SHANWEI': 'SHW',
    # 惠州   497 275
    'HUIZHOU': 'HZO',
    # 盐田   506 257
    'YANTIAN': 'YTA',
    # 赤湾H  513 233
    'CHIWANH': 'CHH',
    # 南沙   496 215
    'NANSHA': 'GNS',  # 注意存在两个南沙
    # 黄埔   491 216
    'HUANGPU': 'HPU',  # 存在两个黄埔，黄埔与黄埔G
    # 珠海   523 216
    'ZHUHAI': 'ZHU',
    # 灯笼山 534 208
    'DENGLONG': 'DLS',
    # 三灶   539 205
    'SANZAO': 'SZA',
}

DICT_STATION_2 = {
    # 芦潮港  10 711
    0: 'LCG',
    # 大戢山  11 730
    1: 'DJS',
    # 金山嘴  17 684
    2: 'JSZ',
    # 滩浒    23 697
    3: 'TXU',
    # 乍浦    26 667
    4: 'ZPU',
    # 澉浦    39 655
    5: 'GPU',
    # 嵊山    17 768
    6: 'SHS',
    # 岱山    46 731
    7: 'DSH',
    # 定海    61 724
    8: 'DHI',
    # 镇海    61 704
    9: 'ZHI',
    # 沈家门  64 737
    10: 'SJM',
    # 北仑    65 727
    11: 'BLN',
    # 乌沙山  90 699
    12: 'WSH',
    # 石浦   106 719
    13: 'SPU',
    # 健跳   117 699
    14: 'JAT',
    # 海门Z  139 687
    15: 'HMZ',
    # 大陈   153 714
    16: 'DCH',
    # 坎门   175 679
    17: 'KMN',
    # 温州S  181 645
    18: 'WZS',
    # 瑞安S  197 641
    19: 'RAS',
    # 鳌江S  206 638
    20: 'AJS',
    # 沙埕S  230 625
    21: 'SCS',
    # 秦屿   238 617
    22: 'QYU',
    # 三沙   246 614
    23: 'SHA',
    # 北礵   258 621
    24: 'BSH',
    # 城澳   263 584
    25: 'CAO',
    # 青屿   279 582
    26: 'QGY',
    # 北茭   278 596
    27: 'BJA',
    # 琯头   293 575
    28: 'GTO',
    # 梅花   299 581
    29: 'MHA',
    # 白岩潭 297 572
    30: 'BYT',
    # 平潭   332 590
    31: 'PTN',
    # 福清核 334 566
    32: 'FQH',
    # 石城   344 562
    33: 'SHC',
    # 峰尾   353 538
    34: 'FHW',
    # 崇武H  368 536
    35: 'CHW',
    # 晋江   382 520
    36: 'JJH',
    # 石井   381 507
    37: 'SJH',
    # 厦门   393 484
    38: 'XMN',
    # 旧镇   421 463
    39: 'JZH',
    # 古雷   432 459
    40: 'GUL',
    # 东山   436 452
    41: 'DSH',
    # 赤石湾 442 434
    42: 'CSW',
    # 云澳   457 427
    43: 'YAO',
    # 汕头S  460 405
    44: 'STO',
    # 海门G  470 397
    45: 'HMN',
    # 惠来   482 392
    46: 'HLA',
    # 陆丰   491 366
    47: 'LFG',
    # 遮浪   501 334
    48: 'ZHL',
    # 汕尾   495 321
    49: 'SHW',
    # 惠州   497 275
    50: 'HZO',
    # 盐田   506 257
    51: 'YTA',
    # 赤湾H  513 233
    52: 'CHH',
    # 南沙   496 215
    53: 'GNS',
    # 黄埔   491 216
    54: 'HPU',
    # 珠海   523 216
    55: 'ZHI',
    # 灯笼山 534 208
    56: 'DLS',
    # 三灶   539 205
    57: 'SZA',
}

# 三区海洋站字典
DICT_STATION_3 = {
    0: 'PTN',
    1: 'FQH',
    2: 'SHC',
    3: 'FHW',
    4: 'CHW',
    5: 'JJH',
    6: 'SJH',
    7: 'XMN',
    8: 'JZH',
    9: 'GUL',
    10: 'DSH',
    11: 'CSW',
    12: 'YAO',
    13: 'STO',
    14: 'HMN',
    15: 'HLA',
    16: 'LFG',
    17: 'ZHL',
    18: 'SHW',
    19: 'HZO',
    20: 'YTA',
    21: 'CWH',
    22: 'NSA',
    23: 'HPU',
    24: 'ZHI',
    25: 'DLS',
    26: 'SZA',
    27: 'BJI',
    28: 'ZHP',
    29: 'SHD',
    30: 'ZJS',
    31: 'ZJS',
    32: 'NAZ',
    33: 'NAD',
    34: 'HAN',
    35: 'XYG',
    36: 'QLN',
    37: 'BAO',
    38: 'GBE',
    39: 'SYA',
    40: 'DFG',
    41: 'STP',
    42: 'WZH',
    43: 'BHI',
    44: 'QZH',
    45: 'FCG',
    46: 'WCH',
    47: 'YGH',

}


class DbFactory:
    """
        数据库工厂
    """

    def __init__(self, db_mapping: str = 'default', engine_str: str = None, host: str = None, post: str = None,
                 db_name: str = None,
                 user: str = None,
                 pwd: str = None):
        db_options = DATABASES.get(db_mapping)
        self.engine_str = engine_str if engine_str else db_options.get('ENGINE')
        self.host = host if host else db_options.get('HOST')
        self.post = post if post else db_options.get('POST')
        self.db_name = db_name if db_name else db_options.get('NAME')
        self.user = user if user else db_options.get('USER')
        self.password = pwd if pwd else db_options.get('PASSWORD')
        # self.engine = create_engine("mysql+pymysql://root:admin123@localhost/searchrescue", encoding='utf-8', echo=True)
        self.engine = create_engine(
            f"mysql+{self.engine_str}://{self.user}:{self.password}@{self.host}:{self.post}/{self.db_name}",
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
    is_del = Column(TINYINT(1), nullable=False, server_default=text("'0'"), default=0)


class IModel(BaseMeta):
    """
        model 抽象父类，主要包含 创建及修改时间
    """
    __abstract__ = True
    gmt_created = Column(DATETIME(fsp=6), default=datetime.datetime.utcnow())
    gmt_modified = Column(DATETIME(fsp=6), default=datetime.datetime.utcnow())


class StationAstronomicTideRealDataModel(IIdModel, IDel, IModel):
    """
        天文潮
    """
    __tablename__ = 'station_astronomictidee _realdata'
    station_code = Column(VARCHAR(200), nullable=False)
    forecast_dt = Column(DATETIME(fsp=2))
    surge = Column(Float, nullable=False)


class StationAlertTideDataModel(IIdModel, IDel, IModel):
    __tablename__ = 'station_stationalerttidemodel'
    station_code = Column(VARCHAR(200), nullable=False)
    alert = Column(Integer, nullable=False)
    tide = Column(Float, nullable=True)


class StationInfoModel(IIdModel, IDel, IModel):
    __tablename__ = 'station_info'
    name = Column(VARCHAR(200), nullable=False)
    code = Column(VARCHAR(200), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    desc = Column(VARCHAR(200), nullable=False)
    pid = Column(Integer)  # 添加的所属父级id
    is_abs = Column(TINYINT(1), nullable=False, server_default=text("'0'"), default=0)  # 是否为抽象对象(抽象对象不显示)
    base_level_diff = Column(Float, nullable=True)
    d85 = Column(Float, nullable=True)


def dict_not_inner(dict1: dict, dict2: dict) -> dict:
    """
        从 dict1 中找到所有不存在于 dict2 中的元素并以字典的形式返回
        return demo: {0: 'LCG', 1: 'DJS', 2: 'JSZ'}
    :param dict1:
    :param dict2:
    :return: demo:  {0: 'LCG', 1: 'DJS', 2: 'JSZ'}
    """
    # dict_diff = {}
    # for key, val in dict1.items():
    #     if val not in dict2:
    #         dict_diff[key] = val
    # return dict_diff
    list_dict1_vals = [val for key, val in dict1.items()]
    list_dict2_vals = [val for key, val in dict2.items()]
    # dict1 中不存在与 dict2 中的 list
    list_dict1_diff_vals = list(set(list_dict1_vals).difference(set(list_dict2_vals)))
    new_dict = {}
    for key, val in dict1.items():
        if val in list_dict1_diff_vals:
            new_dict[key] = val
    return new_dict


def commit_tide(read_data: pd.DataFrame, station_code: str, session, start_dt: datetime.datetime,
                end_dt: datetime.datetime):
    """
        将 dataFrame -> 写入 db
        * 注意在本方法内部会将 start_dt(local) 转换为 utc 时间写入db(db中最终存储的为utc时间)
    :param read_data:
    :param station_code:
    :param session:
    :param start_dt: 该年度的起始时间(local)
    :param end_dt:
    :return:
    """
    index_days = 0
    # start_datetime = datetime.datetime(2021, 1, 1)
    start_datetime = start_dt + datetime.timedelta(hours=-8)
    add_hour = datetime.timedelta(hours=1)
    for day in range(read_data.shape[0]):
        current_date = start_datetime + datetime.timedelta(days=index_days)
        index_days = index_days + 1
        index_hours = 0
        for temp in read_data.iloc[day]:
            if index_hours < 24:
                session.add(StationAstronomicTideRealDataModel(station_code=station_code, surge=temp,
                                                               forecast_dt=current_date + index_hours * add_hour))
                index_hours = index_hours + 1

    session.commit()


def station_2_db(read_dir_path: str, session, dict_station: dict, start_dt: datetime.datetime,
                 end_dt: datetime.datetime, year_str: str):
    """
        将天文潮位文件写入数据库
    :param read_dir_path: 读取路径
    :param session: 数据库 db session
    :param dict_station: 海洋站字典 :{'文件名前缀':'station_code'}
    :param start_dt: 预报起始时间(该年度的起始时间——local时间)
    :param end_dt: 暂时不需要
    :param year_str: 获取  read_dir_path 目录下的文件后缀 一般为 2021|2022 等
    :return:
    """
    # TODO:[-] 22-04-20 新加入的自动遍历站点字典，自动 to db
    # file name eg: SHENGSHAN2022
    for key, val in dict_station.items():
        # 根据 dict_station 获取对应的file_name:
        read_file_full_path: str = pathlib.Path(read_dir_path) / f'{key}{year_str}'
        # C:\Users\evase\OneDrive\同步文件夹\02项目及本子\10-台风集合预报路径系统\数据\2022_天文潮\format_tide_2022\BEIHAI2022
        print(str(read_file_full_path))
        print(key)
        if pathlib.Path(read_file_full_path).exists():
            with open(read_file_full_path, 'rb') as f:
                data_temp: pd.DataFrame = pd.read_table(f, sep='\s+', encoding='unicode_escape', header=None,
                                                        infer_datetime_format=False)
                print(f'读取文件:{read_file_full_path} 成功~')
                commit_tide(data_temp, val, session, start_dt, end_dt)
                print('写入成功')
        else:
            print(f'当前文件:{read_file_full_path},不存在!')


def update_station_d85(dict_station: dict, df: pd.DataFrame, session):
    """
        根据传入的海洋站字典获取对应的从 df 中找到对应的 station_code 获取对向db中更新 d85 field
    :param dict_station:  {'文件名前缀':'station_code'}
    :param df:
    :return:
    """
    station_names = [station_temp[0] for station_temp in dict_station.items()]
    for index in range(df.shape[0]):
        station_temp = df.iloc[index]
        d85_val: float = station_temp['d85']
        if station_temp['code'] in station_names:
            target_station: str = dict_station.get(station_temp['code'])
            # 先根据 code 查一下，然后再 update
            query = session.query(StationInfoModel).filter(StationInfoModel.code == target_station).update(
                {"d85": d85_val})
    session.commit()
    pass


def update_station_alert_level(dict_station: dict, df: pd.DataFrame, session):
    """
        根据传入的海洋站字典从df中找到对应的 station_code ，提取 wl1-wl4 四色警戒潮位值，并减去 d85，写入db
    :param dict_station:
    :param df:
    :param session:
    :return:
    """
    station_names = [station_temp[0] for station_temp in dict_station.items()]
    for index in range(df.shape[0]):
        station_temp = df.iloc[index]
        d85_val: float = station_temp['d85']
        wl1_val: int = station_temp['wl1'] if not pd.isnull(station_temp['wl1']) else None
        wl2_val: int = station_temp['wl2'] if not pd.isnull(station_temp['wl2']) else None
        wl3_val: int = station_temp['wl3'] if not pd.isnull(station_temp['wl3']) else None
        wl4_val: int = station_temp['wl4'] if not pd.isnull(station_temp['wl4']) else None
        if station_temp['code'] in station_names:
            # 注意此处需要从 dict_station 中找到 station_code
            station_code = dict_station.get(station_temp['code'])
            target_station: str = dict_station.get(station_temp['code'])
            # 先根据 code 查一下，然后再 update
            # query = session.query(StationAlertTideDataModel).filter(StationInfoModel.code == target_station).update(
            #     {"d85": d85_val})
            wl1_model = StationAlertTideDataModel(station_code=station_code, tide=wl1_val, alert=5001)
            wl2_model = StationAlertTideDataModel(station_code=station_code, tide=wl2_val, alert=5002)
            wl3_model = StationAlertTideDataModel(station_code=station_code, tide=wl3_val, alert=5003)
            wl4_model = StationAlertTideDataModel(station_code=station_code, tide=wl4_val, alert=5004)
            session.add(wl1_model)
            session.add(wl2_model)
            session.add(wl3_model)
            session.add(wl4_model)

    session.commit()
    pass


def main():
    start_dt: datetime.datetime = datetime.datetime(2022, 1, 1)
    end_dt: datetime.datetime = datetime.datetime(2022, 12, 31)
    year_str: str = '2022'
    read_dir_path: str = r'/opt/data/ignore_data'
    read_dir_path: str = r'C:\Users\evase\OneDrive\同步文件夹\02项目及本子\10-台风集合预报路径系统\数据\2022_天文潮\format_tide_2022'
    session = DbFactory().Session
    # step2: 由于 东海和南海存在部分重叠的台站，需要先录入南海，然后去掉东海中南海已录入的部分，录入两次
    # demo: {0: 'LCG', 1: 'DJS', 2: 'JSZ'}
    dict_diff = dict_not_inner(DICT_STATION_2, DICT_STATION_3)
    # 从DICT_STATION 中过滤对应的 dict
    # {'文件名前缀':'station_code'}
    dict_area2_diff = {}
    list_station_code_area2_diff = [code for key, code in dict_diff.items()]
    for name, code in DICT_STATION.items():
        if code in list_station_code_area2_diff:
            dict_area2_diff[name] = code
    # {'ZHAPU': 'ZPU', 'SHENGSHAN': 'SHS', 'DINGHAI': 'DHI',
    # 'SHENJIAMEN': 'SJM', 'BEILUN': 'BLN', 'WUSS': 'WSH',
    # 'SHIPU': 'SPU', 'JIANTIAO': 'JAT', 'DACHEN': 'DCH',
    # 'KANMEN': 'KMN', 'WENZHOU': 'WZS', 'RUIANA': 'RAS',
    # 'AOJIANG': 'AJS', 'SHACHENG': 'SCS', 'QINYU': 'QYU',
    # 'SANSHA': 'SHA', 'BEISHUANG': 'BSH', 'CHENGAO': 'CAO',
    # 'QINGYU': 'QYU', 'BJIAO': 'BJA', 'GUANTOU': 'GTO', 'MEIHUA':
    # 'MHA', 'BAIYANT': 'BYT', 'CHIWANH': 'CHH', 'NANSHA': 'GNS'}

    # 目前未录入的
    # WENZHOU 2021 年为WENZHOU2
    # RAS
    # QYU 多次录入 注意将 qingyu code -> QGY
    # QGY
    station_2_db(read_dir_path, session, dict_area2_diff, start_dt, end_dt, year_str)

    # 补录几个单站
    # dict_area2_diff = {'QINGYU': 'QGY', 'QINYU': 'QYU', 'RUIAN': 'RAS', 'WENZHOU2': 'WZS'}
    # dict_area2_diff = {'QINGYU': 'QGY',  'RUIAN': 'RAS'}
    # step3: 从指定路径:read_dir_path ,根据 dict_area2_diff 字典中获取存在的文件，并以 start_dt 为起始时间，写入db
    #
    # station_2_db(read_dir_path, session, dict_area2_diff, start_dt, end_dt)
    # + 22-06-23 批量更新 station_info 中的 d85 filed
    read_file_path: str = r'./ignore_data/sites_wl4_四色警戒潮位_含85基面.csv'
    df: pd.DataFrame = pd.read_csv(read_file_path,
                                   names=['name', 'code', 'wl1', 'wl2', 'wl3', 'wl4', 'd85', 'MSL', 'lon', 'lat'])
    # update_station_d85(dict_area2_diff, df, session)
    update_station_alert_level(dict_area2_diff, df, session)
    session.close()
    pass


if __name__ == '__main__':
    main()
