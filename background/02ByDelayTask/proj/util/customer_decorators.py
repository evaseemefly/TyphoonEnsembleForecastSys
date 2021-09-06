# 自定义的各类装饰器

import time
import functools
import logging
from common.enum import JobInstanceEnum
from common.const import UNLESS_ID_STR


def log_count_time():
    """
        记录当前 方法的 执行耗时时间
    @return:
    """

    def outter_log_wrapper(func):
        @functools.wraps(func)
        def inner_log_wrapper(*args, **kwargs):
            start_time = time.time_ns()
            func(*args, **kwargs)
            end_time = time.time_ns()
            print(f'logging:func:{func.__name__},runs count times(ns){end_time - start_time}')

        return inner_log_wrapper

    return outter_log_wrapper


def store_job_rate(level=logging.DEBUG, job_instance=JobInstanceEnum.GET_TY_DETAIL, job_rate=10, name=None,
                   message=None):
    """
        + 21-09-05
            记录当前 job 的进度

    @param level:
    @param job_instance:
    @param job_rate:
    @param name:
    @param message:
    @return:
    """

    def decorate(func):
        logname = name if name else func.__module__
        log = logging.getLogger(logname)
        logmsg = message if message else func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 注意是先执行 func 后在执行写入操作
            celery_id:str= kwargs.get('celery_id',UNLESS_ID_STR)
            res=func(*args, **kwargs)

            print(f'level:{level},job_instance:{job_instance},job_rate:{job_rate}')
            log.log(level, logmsg)

            return res

        return wrapper

    return decorate
