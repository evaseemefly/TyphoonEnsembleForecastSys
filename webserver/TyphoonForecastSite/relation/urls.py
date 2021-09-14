from django.conf.urls import url, include

from rest_framework import routers

# 本项目
from .views import TaskRateByTyView

app_name = '[relation]'

urlpatterns = [
    # 根据 ty 查找对应的 task
    # url(r'^last/rate$', TaskRateByTyView.as_view()),
    url(r'^get/ty/task$', TaskRateByTyView.as_view()),
]
