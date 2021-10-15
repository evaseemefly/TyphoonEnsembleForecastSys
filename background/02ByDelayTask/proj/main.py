#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/13 16:50
# @Author  : evaseemefly
# @Desc    :
# @Site    :
# @File    : settings.py
# @Software: PyCharm

from __future__ import absolute_import, unicode_literals
import os
# TODO:[*] 21-09-27 注意查看一下为何 会是以 root 权限启动?
import sys

os.environ.setdefault('C_FORCE_ROOT', 'true')
SOURCE_PATH = sys.path[0]
sys.path.append(SOURCE_PATH)

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from task.celery import app as celery_app

__all__ = ['celery_app']

if __name__ == '__main__':
    celery_app.start()
    pass
