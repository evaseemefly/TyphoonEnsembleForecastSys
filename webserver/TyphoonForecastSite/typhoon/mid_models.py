from typing import List
from .models import TyphoonForecastRealDataModel
from datetime import datetime


class TyphoonComplexGroupRealDataMidModel:
    def __init__(self, ty_id: int, ty_code: str, area: int, timestamp: str, ty_path_type: str, ty_path_marking: int,
                 bp: float, is_bp_increase: bool, list_realdata: List[TyphoonForecastRealDataModel]):
        self.ty_id = ty_id
        self.ty_code = ty_code
        self.area = area
        self.timestamp = timestamp
        self.ty_path_marking = ty_path_marking
        self.ty_path_type = ty_path_type
        self.bp = bp
        self.is_bp_increase = is_bp_increase
        self.list_realdata = list_realdata


class TyphoonGroupDistMidModel:
    """
        + 21-07-25 新加入的用来作为 台风集合 model 的middel
          desc:
                主要用来存储 台风编号信息及时间戳及创建时间等信息，供检索使用
    """

    def __init__(self, ty_id: int, ty_code: str, timestamp: str, gmt_created: datetime, start: datetime, end: datetime):
        self.ty_id = ty_id
        self.ty_code = ty_code
        self.timestamp = timestamp
        self.gmt_created = gmt_created
        self.forecast_start = start
        self.forecast_end = end

class TyphoonContainsCodeAndStMidModel:
    def __init__(self,ty_code:str,timestamp_str:str):
        self.ty_code=ty_code
        self.timestamp_str=timestamp_str
