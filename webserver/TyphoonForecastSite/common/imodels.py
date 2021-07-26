#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/4 2:58 下午
# @Author  : evaseemefly
# @GithubSit: https://github.com/evaseemefly
# @Site    :
# @Desc    : 所有 接口 model ,抽象 models 的集成父类
# @File    : imodels.py
# @Software: PyCharm
from django.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.utils.timezone import now

# ----
from util.const import DEFAULT_FK, UNLESS_INDEX, DEFAULT_CODE, DEFAULT_STEP, DEFAULT_TIMTSTAMP_STR


class IIdModel(models.Model):
    id = models.AutoField(primary_key=True)

    class Meta:
        abstract = True


class IDelModel(models.Model):
    is_del = models.BooleanField(default=False)

    class Meta:
        abstract = True


class IModel(models.Model):
    """
        model 抽象父类，主要包含 创建及修改时间
    """

    gmt_created = models.DateTimeField(default=now)
    gmt_modified = models.DateTimeField(default=now)

    class Meta:
        abstract = True


class IFileModel(models.Model):
    """
        所有 file 的抽象父类 model
    """
    root_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=200)
    relative_path = models.CharField(max_length=500)
    file_size = models.FloatField(null=True)
    file_ext = models.CharField(max_length=10, null=True)

    class Meta:
        abstract = True


class ITyPathModel(models.Model):
    """
        所有 file 包含台风路径信息的 父类
        maxSurge_TY2022_2021010416_c0_p00.nc  -> c0
    """
    ty_path_type = models.CharField(max_length=3, default=DEFAULT_CODE)
    ty_path_marking = models.IntegerField()

    class Meta:
        abstract = True


class IBpModel(models.Model):
    """
        所有 file 包含 台风气压信息的 父类
        maxSurge_TY2022_2021010416_c0_p00.nc  -> p00
    """
    bp = models.FloatField()
    is_bp_increase = models.BooleanField(default=False)

    class Meta:
        abstract = True


class ISpliceModel(models.Model):
    """
        是否已经进行切片 的 coverage
        若 is_splice = False 则 splice_step 可以为 NULL
    """
    is_splice = models.BooleanField(default=False)
    splice_step = models.IntegerField(default=DEFAULT_STEP, null=True)

    class Meta:
        abstract = True


class ITimeStamp(models.Model):
    timestamp = models.CharField(default=DEFAULT_TIMTSTAMP_STR, max_length=100)

    class Meta:
        abstract = True
