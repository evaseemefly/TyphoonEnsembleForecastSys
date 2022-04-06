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
    def __init__(self, ty_code: str, timestamp_str: str):
        self.ty_code = ty_code
        self.timestamp_str = timestamp_str


class TyphoonGroupRealDataDistMidModel:
    """
        + 21-07-25 新加入的用来作为 台风集合 model 的middel
          desc:
                主要用来存储 台风编号信息及时间戳及创建时间等信息，供检索使用
    """

    def __init__(self, timestamp: int, forecast_dt: datetime, lat: float, lon: float, bp: float, gale_radius: float,
                 ty_path_type: str, ty_path_marking: int, is_bp_increase: bool):
        self.timestamp = timestamp
        self.forecast_dt = forecast_dt
        self.lat = lat
        self.lon = lon
        self.realdata_bp = bp
        self.gale_radius = gale_radius
        self.ty_path_type = ty_path_type
        self.ty_path_marking = ty_path_marking
        self.is_bp_increase = is_bp_increase


class TyphoonComplexGroupDictMidModel:
    def __init__(self, gp_id: int, ty_path_type: str, ty_path_marking: int,
                 bp: float, is_bp_increase: bool, list_realdata: List[TyphoonGroupRealDataDistMidModel]):
        self.gp_id = gp_id
        self.ty_path_type = ty_path_type
        self.ty_path_marking = ty_path_marking
        self.group_bp = bp
        self.is_bp_increase = is_bp_increase
        # self.is_bp_increase = is_bp_increase
        self.list_realdata = list_realdata

class TyDetailMidModel:
    def __init__(self, ty_code: str, id: int, ty_name_en: str = None, ty_name_ch: str = None):
        self.ty_code = ty_code
        self.id = id
        self.ty_name_en = ty_name_en
        self.ty_name_ch = ty_name_ch

    def __str__(self) -> str:
        return f'TyDetailMidModel:id:{self.id}|ty_code:{self.ty_code}|name_en:{self.ty_name_en}|name_ch：{self.ty_name_ch}'


class TyPathMidModel:
    def __init__(self, ty_id: int, ty_code: str, ty_name_en: str, ty_name_ch: str, ty_path_list: [] = []):
        """

        :param ty_id:
        :param ty_code:
        :param ty_name_en:
        :param ty_name_ch:
        :param ty_rate:
        :param ty_stamp:
        """
        self.ty_id = ty_id
        self.ty_code = ty_code
        self.ty_name_en = ty_name_en
        self.ty_name_ch = ty_name_ch
        self.ty_path_list = ty_path_list

        # self.ty_stamp = ty_stamp

    # @property
    # def ty_forecast_dt(self) -> datetime.datetime:
    #     return arrow.get(self.ty_stamp).datetime


class TyForecastRealDataMidModel:
    def __init__(self, lat: float, lon: float, bp: float, ts: int, ty_type: str):
        """

        :param lat:
        :param lon:
        :param bp:
        :param ts:
        :param ty_type:
        """
        self.lat = lat
        self.lon = lon
        self.bp = bp
        self.ts = ts
        self.ty_type = ty_type
