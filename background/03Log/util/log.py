import time
from loguru import logger
from pathlib import Path
from conf.settings import LOG_PATH, LOG_SPLIT_TIME, LOG_EXPIRATION_TIME

project_path = Path.cwd().parent
log_path = Path(project_path, "log")
t = time.strftime("%Y_%m_%d")


# def filter_class(x):
#     dict_level={
#
#     }
#     return '[INFO]' in x['message']


class Loggings:
    __instance = None
    logger.add(f"{LOG_PATH}/info_log_{t}.log", rotation=LOG_SPLIT_TIME, encoding="utf-8", enqueue=True,
               retention=LOG_EXPIRATION_TIME, filter=lambda x: x.get('level').name in ['INFO', 'DEBUG'])
    logger.add(f"{LOG_PATH}/warning_log_{t}.log", rotation=LOG_SPLIT_TIME, encoding="utf-8", enqueue=True,
               retention=LOG_EXPIRATION_TIME, filter=lambda x: x.get('level').name == 'WARNING')
    logger.add(f"{LOG_PATH}/error_log_{t}.log", rotation=LOG_SPLIT_TIME, encoding="utf-8", enqueue=True,
               retention=LOG_EXPIRATION_TIME, filter=lambda x: x.get('level').name == 'ERROR')

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Loggings, cls).__new__(cls, *args, **kwargs)

        return cls.__instance

    def info(self, msg):
        return logger.info(f'{msg}')

    def debug(self, msg):
        return logger.debug(msg)

    def warning(self, msg):
        return logger.warning(f'{msg}')

    def error(self, msg):
        return logger.error(f'{msg}')


log_in = Loggings()
