#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/4 6:11 下午
# @Author  : evaseemefly
# @GithubSit: https://github.com/evaseemefly
# @Site    : 
# @File    : exception.py
# @Software: PyCharm

class NoneError(Exception):
    """
        查询结果为None的错误
    """

    def __init__(self, message, *args, **kwargs):
        self.message = message
        pass


class QueryNoneError(NoneError):
    """
        空查询错误
    """
    def __init__(self, message=None, *args, **kwargs):
        customer_message: str = '查询结果为空' if message is None else message
        super(QueryNoneError, self).__init__(customer_message, *args, **kwargs)

    pass
