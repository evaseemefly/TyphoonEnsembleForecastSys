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
DICT_STATION_2 = {}

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
}
