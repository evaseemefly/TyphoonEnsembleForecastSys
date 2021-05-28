from enum import Enum, unique


@unique
class LayerTypeEnum(Enum):
    GEO_RASTER_LAYER = 1001
    STATION_SURGE_ICON_LAYER = 1002
    TYPHOON_GROUPPATH_LAYER = 1003
