from enum import Enum, unique


@unique
class LayerTypeEnum(Enum):
    GEO_RASTER_LAYER = 1001
    STATION_SURGE_ICON_LAYER = 1002
    TYPHOON_GROUPPATH_LAYER = 1003
    SURGE_MAX_COVERAGE = 1101  # + 21-07-30 新加入的 对应 tb:dict_base 表的枚举
    SURGE_MAX_TIF = 1102
    SURGE_FIELD_COVERAGE = 1103  # 诸时场 nc
    SURGE_FIELD_TIF = 1104  # 逐时场的单个时间提取tif
    SURGE_PRO_COVERAGE = 1105  # 概率增水

@unique
class TaskStateEnum(Enum):
    '''
        对应的是 user_jobuserrate -> state 以及 user_taskinfo -> state

        # TODO:[*] 20-05-07 此处与枚举 users/models.py -> CHOICE_STATUS 相对应，此处如果处理使 enum -> 元祖
    '''
    RUNNING = 1
    COMPLETED = 2
    WAITTING = 3
    ERROR = 4
    UNUSED = 5