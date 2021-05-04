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
    def __init__(self, *args, **kwargs):
        pass