from typing import List
from datetime import datetime


class StationTreeMidModel:
    """
        + 22-09-08 海洋站树形节点数据 model
    """

    def __init__(self, id: int, name: str, code: str, is_abs: bool, sort: int, children):
        self.id = id
        self.name = name
        self.code = code
        self.is_abs = is_abs
        self.sort = sort
        self.children = children


class DistStationTideListMidModel:
    """
        + 23-08-14 配合其他系统获取不同站点的天文潮及时间集合
        serializer 对应 :DistStationTideListSerializer
    """

    def __init__(self, code: str, tide_list: List[float], forecast_ts_list: List[int]):
        self.station_code = code
        self.tide_list = tide_list
        self.forecast_ts_list = forecast_ts_list
