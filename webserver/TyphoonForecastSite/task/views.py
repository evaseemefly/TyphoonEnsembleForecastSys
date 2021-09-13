from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)
from common.view_base import BaseView
from task.tasks import my_task
from util.const import UNLESS_ID, UNLESS_CELERY_ID
from .models import CaseStatusModel
from .serializers import CaseStatusModelSerializer
from util.customer_exception import QueryNoneError


# Create your views here.

class TestView(BaseView):
    def get(self, request: Request) -> Response:
        my_task.delay('ceshi')
        pass


class TaskRateView(BaseView):
    """
        获取指定 celery_id 的对应进度的最后的进度
    """
    def get(self, request: Request) -> Response:
        celery_id_str: str = request.GET.get('celery_id', UNLESS_CELERY_ID)
        # celery_id: int = celery_id_str if celery_id_str is not None else UNLESS_CELERY_ID
        try:
            queryset = CaseStatusModel.objects.filter(celery_id=celery_id_str).order_by('-case_rate').values(
                'celery_id', 'case_state', 'case_rate', 'gmt_created')
            last_task = queryset.first()
            if last_task is None:
                raise QueryNoneError()

            self.json_data = CaseStatusModelSerializer(last_task, many=False).data
            self._status = 200
        except QueryNoneError as qNoneEx:
            self.json_data = qNoneEx.message
        except Exception as ex:
            self.json_data = ex.args
        return Response(self.json_data, self._status)
