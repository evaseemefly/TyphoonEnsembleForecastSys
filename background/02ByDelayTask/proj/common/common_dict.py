# 海洋站 字典
# TODO:[-] 22-01-18 此处
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
    5: 'TXU',
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
    26: 'QYU',
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
    # enum.ForecastAreaEnum.BHI:ForecastArea()
    enum.ForecastAreaEnum.ECS: ForecastArea(19, 31, 110, 129, 1 / 60),
    enum.ForecastAreaEnum.SCS: ForecastArea(15, 26, 105, 123, 1 / 60)
}


def get_forecast_area_range(area: enum.ForecastAreaEnum) -> ForecastArea:
    """
        + 22-06-21 根据区域获取预报的范围
    @param area:
    @return:
    """
    return DICT_FORECAST_AREA.get(area)
