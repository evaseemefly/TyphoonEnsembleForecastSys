from django.conf.urls import url, include

from rest_framework import routers

# 本项目
from .views import TaskCreateView, TaskRateView, TaskRecentNumListView

app_name = '[task]'

urlpatterns = [
    # 根据查询条件获取 typhoonDetailModel 的列表
    url(r'^todo$', TaskCreateView.as_view()),
    url(r'^last/rate$', TaskRateView.as_view()),  # 获取指定任务的最后的进度
    url(r'^last/num/list$', TaskRecentNumListView.as_view()),  # 获取最后的几个任务的进度
    url(r'^last/date/list$', TaskRecentNumListView.as_view()),
    url(r'^model/create$', TaskCreateView.as_view()),
]
