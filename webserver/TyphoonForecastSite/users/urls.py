from django.conf.urls import url, include
from rest_framework_jwt.views import verify_jwt_token, obtain_jwt_token

app_name = '[user]'

urlpatterns = [
    url(r'^api-token-verify/', verify_jwt_token),
    # 切换为 JWT 的验证token的方式
    url('api-token-auth/', obtain_jwt_token),
]