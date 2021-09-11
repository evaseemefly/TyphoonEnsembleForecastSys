# 临时处理的文件
import os
import pathlib
from typing import List
from conf.settings import TEST_ENV_SETTINGS

SHARE_PATH: str = TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR')


def converted_dt_2_timestamp(dt_str: str, timestamp_str: str):
    """
        将 result 目录下的生成的结果文件 的 yyyymmddHHMM 时间戳替换为 timestamp (ns) 的
    @param dt_str:
    @param timestamp_str:
    @return:
    """
    read_path: str = str(pathlib.Path(SHARE_PATH) / dt_str / 'result')
    files = pathlib.Path(read_path).rglob("*")
    files_list: List[str] = []
    for file in files:
        if pathlib.Path.is_file(file):
            files_list.append(str(file))
    for file_name in files_list:
        file_name_split: List[str] = pathlib.Path(file_name).name.split('_')
        file_name_split[2] = timestamp_str

        dir_path: pathlib.Path = pathlib.Path(file_name).parent
        rename_file_name: str = '_'.join(file_name_split)
        rename_file_fullpath: str = str(dir_path / rename_file_name)
        pathlib.Path(file_name).rename(rename_file_fullpath)
        pass
    pass


def main():
    converted_dt_2_timestamp('TY2114_1631327656', "1631327656")
    pass


if __name__ == '__main__':
    main()
