from __future__ import absolute_import
from celery import Celery

from .my_celery import app as celery_app

__all__ = ('celery_app',)
