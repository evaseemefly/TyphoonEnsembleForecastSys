from django.conf.urls import url, include

from rest_framework import routers

# 本项目
from .views import TestView, TaskRateView

app_name = '[task]'

urlpatterns = [
    # 根据查询条件获取 typhoonDetailModel 的列表
    url(r'^todo$', TestView.as_view()),
    url(r'^last/rate$', TaskRateView.as_view()),  # 获取指定任务的最后的进度

]
