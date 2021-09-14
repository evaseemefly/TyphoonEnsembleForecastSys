from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)
from common.view_base import BaseView
from task.tasks import my_task
from .models import RelaTyTaskModel
from task.models import CaseStatusModel
from task.serializers import CaseStatusModelSerializer
from util.const import UNLESS_ID, UNLESS_CELERY_ID
from util.customer_exception import QueryNoneError


# Create your views here.

class TaskRateByTyView(BaseView):
    def get(self, request: Request) -> Response:
        ty_id_str: str = request.GET.get('ty_id', None)
        ty_id: int = UNLESS_ID if ty_id_str is None else int(ty_id_str)
        query = RelaTyTaskModel.objects.filter(ty_id=ty_id)
        try:
            if len(query) > 0:
                celery_id: str = query.first().celery_id
                query_task = CaseStatusModel.objects.filter(celery_id=celery_id).order_by('-case_rate').values(
                    'celery_id', 'case_state', 'case_rate', 'gmt_created')
                last_task = query_task.first()
                self.json_data = CaseStatusModelSerializer(last_task, many=False).data
                self._status = 200
            else:
                raise QueryNoneError
        except QueryNoneError as none_ex:
            print(none_ex.message)
            self.json_data = none_ex.message

        except Exception as ex:
            print(ex.args)
            self.json_data = ex.args
        return Response(self.json_data, self._status)
