# 自定义的各类装饰器

import time
import functools
import logging
import traceback
from util.log import Loggings, log_in


# 异常输出
def except_output(msg='异常'):
    # msg用于自定义函数的提示信息
    def except_execute(func):
        @functools.wraps(func)
        def execept_logoin(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                sign = '=' * 60 + '\n'
                log_in.error(f'异常函数:{func.__name__}{msg}：{e}')
                log_in.error(f'异常代码:\n{sign}{traceback.format_exc()}{sign}')

        return execept_logoin

    return except_execute
