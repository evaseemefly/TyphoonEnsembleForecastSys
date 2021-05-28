from datetime import datetime

from abc import ABCMeta, abstractmethod


class ICheckExisted(metaclass=ABCMeta):
    """
        + 21-05-28 加入的 检查是否存在对应数据的 接口类
    """
    @abstractmethod
    def check_existed(self, ty_code: str, timestamp: str, forecast_dt: datetime) -> bool:
        pass
