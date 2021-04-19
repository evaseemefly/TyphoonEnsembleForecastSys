"""TyphoonForecastSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    # 切换为 JWT 的验证token的方式
    path('api-token-auth/', obtain_jwt_token),
    # jwt的认证接口
    path('login/', obtain_jwt_token),
    url('^users/', include(('users.urls', "auth"), namespace="user")),
    url('^typhoon/', include(('typhoon.urls', "typhoon"), namespace="typhoon")),
]
