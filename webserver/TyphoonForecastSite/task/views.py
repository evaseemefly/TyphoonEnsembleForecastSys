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


class TaskRecentNumListView(BaseView):
    """
        获取最近的 num 个 task 作业进度列表
    """
    num: int = 10
    max_num: int = 20

    def get(self, request: Request) -> Response:
        num_str: str = request.GET.get('num', None)
        num: int = int(num_str) if num_str is not None else self.num
        if num > self.max_num:
            num = self.max_num
        rate_list = []
        try:
            # list_celery_ids = []
            list_celery_ids = list(CaseStatusModel.objects.values('celery_id').distinct())[-num:]
            if len(list_celery_ids) == 0:
                raise QueryNoneError()
            for temp_celery in list_celery_ids:
                temp_celery_id: str = temp_celery.get('celery_id')
                temp_task: CaseStatusModel = CaseStatusModel.objects.filter(celery_id=temp_celery_id).order_by(
                    '-case_rate').values('celery_id', 'case_state', 'case_rate', 'gmt_created').first()
                rate_list.append(temp_task)

            self.json_data = CaseStatusModelSerializer(rate_list, many=True).data
            self._status = 200
        except QueryNoneError as qNoneEx:
            self.json_data = qNoneEx.message
        except Exception as ex:
            self.json_data = ex.args
        return Response(self.json_data, self._status)

    pass


class TaskRecentDateStatisticsListView(BaseView):
    """
        获取 最近 几日的创建的作业的统计列表
        step:
         -1 获取最近 num 的日期列表
         -2 根据指定日期获取该日期所创建的 task 的 celery_id
         -3 获取该日的 celery_id 的总数
    """
    pass



