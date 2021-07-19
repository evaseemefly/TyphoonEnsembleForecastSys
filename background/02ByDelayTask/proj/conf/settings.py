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
    # 'TY_GROUP_PATH_ROOT_DIR': r'E:\02data\03typhoon',  # win
    'TY_GROUP_PATH_ROOT_DIR': r'E:\02data\05docker-data\docker-shared\ty_docker',
    # 加入了 docker 的映射路径，目前docker环境有一些问题，暂时使用此种方式
    # 'TY_GROUP_PATH_ROOT_DIR': r'/Users/liusihan/data/typhoon_data/'  # mac
    # 'TY_GROUP_PATH_ROOT_DIR': r'/my_shared_data/pathfiles/',
    'TY_CODE': 'TD04',
    # 'TY_TIMESTAMP': '2021010416'
    'TY_TIMESTAMP': '2021071908'
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
