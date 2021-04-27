# + 21-04-24
import typing
from typing import List
from model.models import TyphoonGroupPathModel
from core.db import DbFactory


class StationSurgeRealDataFile:
    def __init__(self, dir_path: str, file_name: str):
        """
            海洋站 潮位站 数据 file
        @param dir_path:
        @param file_name: Surge_TY2022_2021010416_f0_p10.dat or Surge_TY2022_2021010416_c0_p_05.dat
        """
        self.dir_path = dir_path
        self.file_name = file_name  # Surge_TY2022_2021010416_f0_p10.dat or Surge_TY2022_2021010416_c0_p_05.dat

    @property
    def name_split(self) -> List[str]:
        """
            将 self.file_name 按照 split_stamp 切分为数组,注意去掉了后缀 .dat 后的文件名称
            去掉了 Surge ，保持与 GroupTyPath 相同的 name_split
            ['Surge', 'TY2022', '2021010416', 'f0', 'p10']
            or
            ['Surge', 'TY2022', '2021010416', 'c0', 'p', '05']
        @return:  ['TY2022', '2021010416', 'c0', 'p', '05'] or ['Surge', 'TY2022', '2021010416', 'c0', 'p', '05']
        """
        # [['Surge', 'TY2022', '2021010416', 'c0', 'p', '05.dat']]
        # - >
        # ['Surge', 'TY2022', '2021010416', 'c0', 'p', '05']
        list_split: List[str] = []
        split_stamp: str = '_'  # 分隔符
        if self.file_name:
            full_name_remove_ext: str = self.file_name[:self.file_name.find('.')]  # 移除了后缀的文件名
            list_split = full_name_remove_ext.split(split_stamp)[1:]  # ['TY2022', '2021010416', 'c0', 'p', '05']
        return list_split

    @property
    def ty_code(self) -> str:
        """
            获取 台风 code
            TODO:[*] 21-04-23 此处与 GroupTyPath 相同，可去掉
        @return:
        """
        code: str = None
        if len(self.name_split) > 0:
            # TY1822 -> 1822
            code = self.name_split[0][2:]
        return code

    @property
    def ty_timestamp(self) -> str:
        """
            获取 台风的时间戳
        @return:
        """
        ts_str: str = None
        if len(self.name_split) > 1:
            ts_str = self.name_split[1]
        return ts_str

    @property
    def ty_bp_stamp(self) -> str:
        """
            获取 台风 气压 标识
            eg: TY1822_2020042710_l5_p05 -> p05
        @return:
        """
        temp_stamp: str = None
        if len(self.name_split) > 3:
            if len(self.name_split) > 4:
                temp_stamp: str = f'{self.name_split[3]}_{self.name_split[4]}'
            else:
                temp_stamp: str = self.name_split[3]
        return temp_stamp

    @property
    def ty_bp_is_increase(self) -> bool:
        """
            获取 气压的 是否为增量
            eg: TY1822_2020042710_l5_p05 -> true

        @return:
        """
        stamp: str = '_'
        if self.ty_bp_stamp.find(stamp) >= 0:
            return False
        else:
            return True

    @property
    def ty_bp_val(self) -> int:
        """
            获取 group file 的 偏移气压值
            eg: TY1822_2020042710_l5_p05 -> 05
        @return:
        """
        return int(self.ty_bp_stamp[-2:])

    @property
    def ty_path_stamp(self) -> str:
        """
            获取 台风路径 标志
            eg: TY1822_2020042710_l5_p05 -> l5
        @return:
        """
        path_type: str = None
        if len(self.name_split) > 1:
            path_type = self.name_split[2]
        return path_type

    @property
    def ty_path_type(self) -> str:
        return self.ty_path_stamp[:1].lower()

    @property
    def ty_path_marking(self) -> int:
        return int(self.ty_timestamp[1:])

    def get_pg(self, ty_id: int) -> TyphoonGroupPathModel:
        """
            + 21-04-26 注意此处 还需要传入 ty_id ，因为不同的 ty 可能会有以下查询参数相同的问题(包括 ty_code)
        @param ty_id: 台风 id
        @return:
        """
        session = DbFactory().Session
        query_gp = session.query(TyphoonGroupPathModel).filter(
            TyphoonGroupPathModel.ty_code == self.ty_code, TyphoonGroupPathModel.timestamp == self.ty_timestamp,
            TyphoonGroupPathModel.ty_path_type == self.ty_path_type,
            TyphoonGroupPathModel.ty_path_marking == self.ty_path_marking, TyphoonGroupPathModel.bp == self.ty_bp_val,
            TyphoonGroupPathModel.is_bp_increase == self.ty_bp_is_increase,
            TyphoonGroupPathModel.ty_id == ty_id)
        res: TyphoonGroupPathModel = query_gp.first()
        return res
