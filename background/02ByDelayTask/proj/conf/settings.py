#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/13 16:50
# @Author  : evaseemefly
# @Desc    :
# @Site    :
# @File    : settings.py
# @Software: PyCharm

# 测试环境配置
TEST_ENV_SETTINGS = {
    'TY_GROUP_PATH_ROOT_DIR': r'E:\02data\03typhoon',  # win
    # 'TY_GROUP_PATH_ROOT_DIR': r'/Users/liusihan/data/typhoon_data/'  # mac
}

# 数据库的配置，配置借鉴自 django 的 settings 的结构
DATABASES = {
    'default': {
        'ENGINE': 'mysqldb',  # 数据库引擎
        'NAME': 'typhoon_forecast_db',  # 数据库名
        # by casablanca
        # mac
        'USER': 'root',  # 账号
        # 7530,mac
        # 'PASSWORD': 'admin123',
        # 5820,p52s,p500,razer
        'PASSWORD': '123456',
        # by cwb
        # 'USER': 'root',  # 账号
        # 'PASSWORD': '123456',
        'HOST': '127.0.0.1',  # HOST
        'POST': 3306,  # 端口
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
        },
    }
}
