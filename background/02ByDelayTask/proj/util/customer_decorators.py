# 自定义的各类装饰器

import time
import functools
import logging
from common.enum import JobInstanceEnum
from common.const import UNLESS_ID_STR
from local.globals import get_celery
from model.models import CaseStatus
from core.db import DbFactory
from util.log import Loggings, log_in

session = DbFactory().Session


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

            celery_id: str = UNLESS_ID_STR
            if len(args) > 0 and hasattr(args[0], 'request'):
                celery_id = args[0].request.get('id')
            get_celery().celery_id = celery_id if get_celery().celery_id == UNLESS_ID_STR else UNLESS_ID_STR
            local_celery_id = get_celery().celery_id
            log_in.info(msg=f'当前接收到的延时任务task_id:{local_celery_id}')
            # TODO:[-] 21-09-07 加入 task 持久化保存功能
            # celery_id:str= kwargs.get('celery_id',UNLESS_ID_STR)
            case = CaseStatus(celery_id=local_celery_id, case_state=job_instance.value, case_rate=job_rate)
            session.add(case)
            session.commit()
            res = func(*args, **kwargs)
            log_in.info(f'level:{level},job_instance:{job_instance},job_rate:{job_rate}')
            # log.log(level, logmsg)

            return res

        return wrapper

    return decorate
