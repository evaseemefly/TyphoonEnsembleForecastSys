from django.conf.urls import url, include

from rest_framework import routers

# 本项目
from .views import LayerCheckView, ConsulView

app_name = '[common]'

urlpatterns = [
    # 根据查询条件获取 typhoonDetailModel 的列表
    url(r'^layers/check$', LayerCheckView.as_view()),
    url(r'^consul/check$', ConsulView.as_view()),

]
