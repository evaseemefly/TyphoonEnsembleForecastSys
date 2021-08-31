from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)
from common.view_base import BaseView
from task.tasks import my_task


# Create your views here.

class TestView(BaseView):
    def get(self, request: Request) -> Response:
        my_task.delay('ceshi')
        pass
