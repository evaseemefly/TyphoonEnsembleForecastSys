import time
from loguru import logger
from pathlib import Path
from conf.settings import LOG_PATH, LOG_SPLIT_TIME, LOG_EXPIRATION_TIME

project_path = Path.cwd().parent
log_path = Path(project_path, "log")
t = time.strftime("%Y_%m_%d")


class Loggings:
    __instance = None
    logger.add(f"{LOG_PATH}/interface_log_{t}.log", rotation=LOG_SPLIT_TIME, encoding="utf-8", enqueue=True,
               retention=LOG_EXPIRATION_TIME)

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Loggings, cls).__new__(cls, *args, **kwargs)

        return cls.__instance

    def info(self, msg):
        return logger.info(msg)

    def debug(self, msg):
        return logger.debug(msg)

    def warning(self, msg):
        return logger.warning(msg)

    def error(self, msg):
        return logger.error(msg)


