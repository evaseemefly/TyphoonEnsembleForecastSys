from typing import List
from .models import TyphoonForecastRealDataModel


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
