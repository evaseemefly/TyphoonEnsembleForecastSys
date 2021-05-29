class TyExistedStatusMidModel:
    def __init__(self, geo_raster_is_existed: bool, station_realdata_is_existed: bool, ty_group_path_is_existed: bool):
        self.geo_raster_status = geo_raster_is_existed
        self.station_realdata_staus = station_realdata_is_existed
        self.ty_group_path_status = ty_group_path_is_existed
