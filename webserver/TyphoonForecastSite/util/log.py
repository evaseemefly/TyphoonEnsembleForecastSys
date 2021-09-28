import pathlib
import time
from loguru import logger
from pathlib import Path
from TyphoonForecastSite.settings import LOG_LOGURU

# project_path = Path.cwd().parent
# log_path = Path(project_path, "log")
t = time.strftime("%Y_%m_%d")

LOG_PATH = LOG_LOGURU.get('LOG_PATH')
LOG_SPLIT_TIME = LOG_LOGURU.get('LOG_SPLIT_TIME')
LOG_EXPIRATION_TIME = LOG_LOGURU.get('LOG_EXPIRATION_TIME')

# 此处加入判断判断指定的目录是否存在，不存在则创建该目录
path = pathlib.Path(LOG_PATH)
if not path.exists():
    path.mkdir(parents=True)


class Loggings:
    """
        + 21-09-28 通过 loguru 实现的 logo 日志工具类
                   封装了 - info -debug -warning -error 方法
    """
    __instance = None
    logger.add(f"{LOG_PATH}/interface_log_{t}.log", rotation=LOG_SPLIT_TIME, encoding="utf-8", enqueue=True,
               retention=LOG_EXPIRATION_TIME)

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Loggings, cls).__new__(cls, *args, **kwargs)

        return cls.__instance

    def info(self, msg: str) -> logger:
        return logger.info(msg)

    def debug(self, msg: str) -> logger:
        return logger.debug(msg)

    def warning(self, msg: str) -> logger:
        return logger.warning(msg)

    def error(self, msg: str) -> logger:
        return logger.error(msg)


log_in = Loggings()
