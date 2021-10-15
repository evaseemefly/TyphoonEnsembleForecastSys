#!/bin/sh

# python manage.py migrate
/opt/conda/envs/py37/bin/celery -A .main worker --pool=solo -l info
# 改为在宿主机上运行
/public/home/surge/apps/anaconda3/envs/py37/bin/celery -A main worker --pool=solo -l info