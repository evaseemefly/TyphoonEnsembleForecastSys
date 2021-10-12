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
    # 'TY_GROUP_PATH_ROOT_DIR': r'E:\05DATA\01nginx_data\nmefc_download\TY_GROUP_RESULT',  # T7920
    'TY_GROUP_PATH_ROOT_DIR': r'/my_shared_data',  # + 21-09-28 docker 需要与宿主机指定路径映射的路径
    # 'TY_GROUP_PATH_ROOT_DIR': r'/Users/evaseemefly/04data/01nginx_data/nmefc_download/TY_GROUP_RESULT',  # mac-m1
    # + 21-08-02 数据处理统一在 nginx 目录下
    # 'TY_GROUP_PATH_ROOT_DIR': r'D:\03nginx_data\nmefc_download\TY_GROUP_RESULT',  # p5750
    # 'TY_GROUP_PATH_ROOT_DIR': r'F:\03nginx_data\nmefc_download\TY_GROUP_RESULT',  # 7530
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
        # 'PASSWORD': '12345678',
        # 5820,p52s,p500,razer
        'PASSWORD': '123456',
        # 'HOST': '127.0.0.1',  # HOST
        # 'HOST': '172.18.0.1',  # HOST
        # 访问宿主的mysql服务,
        # 'HOST': 'host.docker.internal',
        'HOST': 'localhost',  # HOST
        'POST': 3306,  # 端口
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
        },
    }
}

# + 21-09-28 新加入的 loguru 的配置文件
LOG_LOGURU = {
    # 'LOG_PATH': r'E:\05DATA\99test\05log',  # 日志文件路径
    'LOG_PATH': r'/log',  # 日志文件路径
    'LOG_SPLIT_TIME': '1 day',
    'LOG_EXPIRATION_TIME': '30 days',
}

JOB_SETTINGS = {
    'MAX_TIME_INTERVAL': 3600  # 计算任务允许的最大时间(单位:s)
}

# TODO:[-] 21-08-31 celery 相关配置

# 使用RabbitMQ作为消息代理
# CELERY_BROKER_URL = f'amqp://guest:guest@localhost:5672/'
# CELERY_BROKER_URL = f'amqp://guest:guest@rabbitmq:5672/'
# 针对mac使用 redis 作为消息代理
CELERY_BROKER_URL = f'redis://redis:6379/0'
# 把任务结果存在了Redis
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
# 任务序列化和反序列化使用JSON方案
CELERY_TASK_SERIALIZER = 'pickle'
# 读取任务结果使用JSON
CELERY_RESULT_SERIALIZER = 'json'
# 任务过期时间，不建议直接写86400，应该让这样的magic数字表述更明显
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
# 指定接受的内容类型，是个数组，可以写多个
CELERY_ACCEPT_CONTENT = ['json', 'pickle']

# CELERY_worker_cancel_long_running_tasks_on_connection_loss = True

# CELERY_BROKER_CONNECTION_RETRY = False
CELERY_BROKER_HEARTBEAT = 30 * 60
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 43200}
