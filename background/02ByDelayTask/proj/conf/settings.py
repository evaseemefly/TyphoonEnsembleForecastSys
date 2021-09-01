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
    # 'TY_GROUP_PATH_ROOT_DIR': r'E:\02data\05docker-data\docker-shared\ty_docker',  # P5750
    # 'TY_GROUP_PATH_ROOT_DIR': r'D:\05DATA\05docker-data\ty-docker',  # P1
    # + 21-08-02 数据处理统一在 nginx 目录下
    # 'TY_GROUP_PATH_ROOT_DIR': r'D:\03nginx_data\nmefc_download\TY_GROUP_RESULT',  # p5750
    'TY_GROUP_PATH_ROOT_DIR': r'F:\03nginx_data\nmefc_download\TY_GROUP_RESULT',  # 7530
    # 加入了 docker 的映射路径，目前docker环境有一些问题，暂时使用此种方式
    # 'TY_GROUP_PATH_ROOT_DIR': r'/Users/liusihan/data/typhoon_data/'  # mac
    # 'TY_GROUP_PATH_ROOT_DIR': r'/my_shared_data/pathfiles/',
    'TY_CODE': '2022',
    # 'TY_TIMESTAMP': '2021010416'
    'TY_TIMESTAMP': '2021010416',
    # TODO:[-] 21-07-30 暂时加入的台风的年份的头两位
    'YEAR_HEADER': '20'
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

# TODO:[-] 21-08-31 celery 相关配置

# 使用RabbitMQ作为消息代理
CELERY_BROKER_URL = f'amqp://guest:guest@localhost:5672/'
# 把任务结果存在了Redis
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# 任务序列化和反序列化使用JSON方案
CELERY_TASK_SERIALIZER = 'pickle'
# 读取任务结果使用JSON
CELERY_RESULT_SERIALIZER = 'json'
# 任务过期时间，不建议直接写86400，应该让这样的magic数字表述更明显
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
# 指定接受的内容类型，是个数组，可以写多个
CELERY_ACCEPT_CONTENT = ['json', 'pickle']