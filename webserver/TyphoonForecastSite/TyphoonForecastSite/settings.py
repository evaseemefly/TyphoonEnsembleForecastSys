"""





Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from ._PRIVACY import DB
from enum import Enum, unique

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^belj%#qs2a$bo&*xs9p*@rs76qwst@+x4a%a^3nl5%!pyb2xu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# TODO:[-] 21-10-13 添加实际线上环境
ALLOWED_HOSTS = ['128.5.10.21', '127.0.0.1', '0.0.0.0', 'localhost', '192.168.50.86', '128.5.9.79']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'typhoon',
    'station',
    'common',
    'users',
    'geo',
    'task',
    'relation'
]
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TyphoonForecastSite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'TyphoonForecastSite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

@unique
class PATTERNENUM(Enum):
    HOME = 1
    COMPANY = 2
    DOCKER = 3


# 未提交的数据库密码(请勿提交)
DB_PWD = DB.get('DB_PWD')
# 调试时需要修改此处
PATTERN = PATTERNENUM.COMPANY

HOST = '127.0.0.1'
if PATTERN == PATTERNENUM.COMPANY:
    HOST = '128.5.10.21'
elif PATTERN == PATTERNENUM.DOCKER:
    HOST = 'host.docker.internal'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
        'NAME': 'typhoon_forecast_db',  # 数据库名
        # 'NAME': 'typhoon_forecast_db_new',  # 数据库名 home 中的db修改为 new
        # by casablanca
        # mac
        'USER': 'root',  # 账号
        # 7530,mac
        # 'PASSWORD': '12345678',
        # 5820,p52s,p500,razer
        'PASSWORD': DB_PWD if PATTERN == PATTERNENUM.COMPANY else '123456',
        # 'HOST': '127.0.0.1',  # HOST
        # 'HOST': '0.0.0.0',  # HOST
        # 'HOST': '128.5.10.21',  # HOST
        # TODO:[-] 23-6-27 consul服务注册
        'HOST': '128.5.9.79',  # HOST
        # 访问宿主的mysql服务,
        # 'HOST': 'mysql',  # TODO:[-] 21-10-11 注意此处使用 mysql 的容器
        # mac 环境下 (1049, "Unknown database 'typhoon_forecast_db'")
        # 'HOST': 'host.docker.internal',  # docker访问宿主机的mysql服务
        # 'HOST': '127.0.0.1',
        # 'HOST': HOST,
        # 'PORT': '3308' if PATTERN == PATTERNENUM.COMPANY else '3306',  # 端口
        'PORT': '3306',

        # 'PORT': 3308,  # TODO:[-] 21-10-11 端口暂时改为 3308
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

MY_PAGINATOR = {
    'PAGE_INDEX': 1,
    'PAGE_COUNT': 10
}

# TODO:[-] 20-11-03 加入的测试时使用的读取存储文件的网络存储的相关信息
STORE_OPTIONS = {
    # 'URL': '128.5.10.21',
    'URL': '192.168.50.86',
    # 'URL': 'localhost',
    'HOST': 82,  # TODO:[-] 21-01-03 暂时将 nginx 的端口改为了 82 ，注意！
    'STORE_COMMON_BASE': 'images',  # 对应 nginx 的映射的根目录
    'HEAD': 'nmefc_download',  # nginx 实际存储的 起始路径
}
# TODO:[-] 21-08-01 由于不同的数据中间还会继续分层，所以引入了 STORE_RELATIVE_PATH_OPTIONS
# TODO:[-] 21-08-01 由于不同的数据中间还会继续分层，所以引入了 STORE_RELATIVE_PATH_OPTIONS
STORE_RELATIVE_PATH_OPTIONS = {
    'TY_GROUP_CASE': 'TY_GROUP_RESULT/'
}
# TODO:[-] 21-05-24 手动添加 gdal lib 的地址
# TODO:[-] 21-03-27 mac 可以去掉此部分
# + 21-07-21 P7530
# GDAL_LIBRARY_PATH = r'D:\01Setup\ANACONDA\envs\new_oil_gdal\Library\bin\gdal301'

# + 21-08-11 T5820
GDAL_LIBRARY_PATH = r'C:\Users\evase\Anaconda3\envs\new_oil_gdal\Library\bin\gdal301'
# P5750
# TODO:[*] 21-07-21 注意此处有可能会出现无法找到该dll的文件的情况
# GDAL_LIBRARY_PATH = r'D:\01Setup\ANACONDA\envs\new_oil_gdal\Library\bin\gdal301'

# TODO:[-] 21-07-26 P1 环境备份
# GDAL_LIBRARY_PATH = r'C:\Users\evase\Anaconda3\envs\new_oil_gdal\Library\bin\gdal301'


# TODO:[-] 21-07-25 P5750 环境备份
# GDAL_LIBRARY_PATH = r'C:\Users\evase\.conda\envs\new_oil_gdal\Library\bin\gdal301'

# TODO:[-] 21-07-22 P5750 环境备份
# GDAL_LIBRARY_PATH = r'C:\Users\evase\Anaconda3\envs\new_oil_gdal\Library\bin\gdal301'

# TODO:[-] 21-08-31 celery 相关配置

# 使用RabbitMQ作为消息代理
# CELERY_BROKER_URL = f'amqp://guest:guest@localhost:5672/'
# 把任务结果存在了Redis
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# TODO:[-] 22-01-19 线上环境的 celery redis配置
# CELERY_BROKER_URL = f'redis://redis:6379/0'
# TODO:[*] 22-01-19 本地使用docker中的redis服务
CELERY_BROKER_URL = f'redis://host.docker.internal:6379/0'
# 任务序列化和反序列化使用JSON方案
CELERY_TASK_SERIALIZER = 'pickle'
# 读取任务结果使用JSON
CELERY_RESULT_SERIALIZER = 'json'
# 任务过期时间，不建议直接写86400，应该让这样的magic数字表述更明显
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
# 指定接受的内容类型，是个数组，可以写多个
CELERY_ACCEPT_CONTENT = ['json', 'pickle']

# + 21-09-28 新加入的 loguru 的配置文件
LOG_LOGURU = {
    # 'LOG_PATH': r'E:\05DATA\99test\05log',  # 日志文件路径
    'LOG_PATH': r'/log',  # 日志文件路径
    'LOG_SPLIT_TIME': '1 day',
    'LOG_EXPIRATION_TIME': '30 days',
}

PROJ_VERSIONS = 'title:typhoon_django_server,content:typhoon drf server,version:1.5'
