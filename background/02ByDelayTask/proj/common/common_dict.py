# 海洋站 字典
# TODO:[-] 22-01-18 此处
import numpy as np
from typing import List

from common import enum


def get_area_dict_station(area: enum.ForecastAreaEnum) -> dict:
    current_dict = DICT_STATION
    if area == enum.ForecastAreaEnum.BHI:
        current_dict = DICT_STATION_1
    elif area == enum.ForecastAreaEnum.ECS:
        current_dict = DICT_STATION_2
    elif area == enum.ForecastAreaEnum.SCS:
        current_dict = DICT_STATION_3
    return current_dict


DICT_STATION = {
    0: 'SHW',
    1: 'HZO',
    2: 'YTA',
    3: 'DSH',
    4: 'NAO',
    5: 'DMS',
    6: 'SHK',
    7: 'CWH',
    8: 'QHW',
    9: 'SZJ'

}

DICT_STATION_1 = {
    # 东港    71 431
    0: 'DGG',
    1: 'XCS',
    2: 'LHT',
    3: 'BYQ',
    4: 'YKO',
    5: 'HLD',
    6: 'ZMW',
    7: 'QHD',
    8: 'TGU',
    9: 'CFD',
    10: 'HHA',
    11: 'BZG',
    12: 'DYG',
    13: 'YJG',
    14: 'WFG',
    15: 'LKO',
    16: 'PLI',
    17: 'YTI',
    18: 'XSD',
    19: 'CST',
    20: 'WDG',
    21: 'SID',
    22: 'QLY',
    23: 'WMT',
    24: 'XMD',
    25: 'RZH',
    26: 'LSH',
    27: 'LYG',
    28: 'YWI',
    29: 'YKG',
    30: 'LSI',
    31: 'BZH',
    32: 'WSG',
    33: 'GQA',
    34: 'CMG',
    # 芦潮港  10 711
    35: 'LCG',
    # 3 大戢山  11 730
    36: 'DJS',
    # 3 金山嘴  17 684
    37: 'JSZ',
    # 3 滩浒    23 697
    38: 'TXU',
    # 3 乍浦    26 667
    39: 'ZPU',
    # 3 澉浦    39 655
    40: 'GPU',
    # 4 嵊山    17 768
    41: 'SHS',
    # 4 岱山    46 731
    42: 'DSH',
    # 4 定海    61 724
    43: 'DHI',
    # 4 镇海    61 704
    44: 'ZHI',
    # 沈家门  64 737
    45: 'SJM',
    # 北仑    65 727
    46: 'BLN',
    # 乌沙山  90 699
    47: 'WSH',
    # 石浦   106 719
    48: 'SPU',
    # 健跳   117 699
    49: 'JAT',
    # 海门Z  139 687
    50: 'HMZ',
    # 大陈   153 714
    51: 'DCH',
    # 坎门   175 679
    52: 'KMN',
    # 温州S  181 645
    53: 'WZS',
    # 瑞安S  197 641
    54: 'RAS',
    # 鳌江S  206 638
    55: 'AJS',
    # 沙埕S  230 625
    56: 'SCS',
    # 秦屿   238 617
    57: 'QYU',
    # 三沙   246 614
    58: 'SHA',
    # 北礵   258 621
    59: 'BSH',
    # 城澳   263 584
    60: 'CAO',
    # 青屿   279 582
    61: 'QGY',
    # 北茭   278 596
    62: 'BJA',
    # 琯头   293 575
    63: 'GTO',
    # 梅花   299 581
    64: 'MHA',
    # 白岩潭 297 572
    65: 'BYT',
    # 平潭   332 590
    66: 'PTN',
    # 福清核 334 566
    67: 'FQH',
    # 石城   344 562
    68: 'SHC',
    # 峰尾   353 538
    69: 'FHW',
    # 崇武H  368 536
    70: 'CHW',
    # 晋江   382 520
    71: 'JJH',
    # 石井   381 507
    72: 'SJH',
    # 厦门   393 484
    73: 'XMN',
    # 旧镇   421 463
    74: 'JZH',
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
    55: 'ZHU',
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
    21: 'CHH', # 赤湾 CWH -> CHH
    22: 'NSA',
    23: 'HPU',
    24: 'ZHU', # 珠海 ZHI -> ZHU
    25: 'DLS',
    26: 'SZA',
    27: 'BJN', # BJI -> BJN
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


class ForecastArea:
    """
        预报区域model
    """

    def __init__(self, lat_min: float, lat_max: float, lon_min: float, lon_max: float, step: float):
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.step = step


# 预报范围字典
DICT_FORECAST_AREA = {
    enum.ForecastAreaEnum.BHI: ForecastArea(24, 41, 117, 129, 1 / 60),
    enum.ForecastAreaEnum.ECS: ForecastArea(19, 31, 110, 129, 1 / 60),
    enum.ForecastAreaEnum.SCS: ForecastArea(15, 26, 105, 123, 1 / 60)
}


def get_forecast_area_latlngs(area: enum.ForecastAreaEnum) -> List[np.ndarray]:
    """
        + 22-07-14 获取经纬度范围
    @param area:
    @return:[lats, lngs]
    """
    lats = None
    lngs = None
    if area == enum.ForecastAreaEnum.BHI:
        lngs = np.arange(117 + 1 / 120, 129 + 1 / 120, 1 / 60)
        lats = np.arange(24 + 1 / 120, 41 + 1 / 120, 1 / 60)
    elif area == enum.ForecastAreaEnum.ECS:
        lngs = np.arange(110 + 1 / 120, 129 + 1 / 120, 1 / 60)
        lats = np.arange(19 + 1 / 120, 31 + 1 / 120, 1 / 60)
    elif area == enum.ForecastAreaEnum.SCS:
        lngs = np.arange(105 + 1 / 120, 123 + 1 / 120, 1 / 60)
        lats = np.arange(15 + 1 / 120, 26 + 1 / 120, 1 / 60)
    return [lats, lngs]


def get_forecast_area_range(area: enum.ForecastAreaEnum) -> ForecastArea:
    """
        + 22-06-21 根据区域获取预报的范围
    @param area:
    @return:
    """
    return DICT_FORECAST_AREA.get(area)
