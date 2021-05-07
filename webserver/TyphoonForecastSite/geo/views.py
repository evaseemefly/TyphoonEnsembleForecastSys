from django.shortcuts import render
from django.shortcuts import render
import pathlib
from datetime import datetime
from os import path
from typing import List

import arrow
from django.shortcuts import render
from django.core.serializers import serialize
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)
import arrow

from .views_base import RasterBaseView
from util.const import DEFAULT_NULL_KEY
from util.exception import NoneError


# Create your views here.

class GeoTiffView(RasterBaseView):
    def get(self, request: Request) -> Response:
        id: int = int(request.GET.get('id')) if request.GET.get('id', None) else DEFAULT_NULL_KEY
        ty_code: str = request.GET.get('ty_code', None)
        ty_timestamp_str: str = request.GET.get('ty_timestamp', None)
        # ty_timestamp: datetime = arrow.get(ty_timestamp_str).datetime
        try:
            self.json_data = self.get_tif_url(request, id=id, ty_code=ty_code, timestamp=ty_timestamp_str)
            self._status = 200
        except NoneError as noneErr:
            self.json_data = noneErr.args
        except  Exception as e:
            self.json_data = e.args
        return Response(self.json_data, status=self._status)