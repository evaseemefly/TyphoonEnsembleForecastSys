from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import (APIView, api_view,
                                       authentication_classes,
                                       permission_classes)

# 其与的第三方库
import arrow

from .view_base import BaseView
from .mid_models import TyExistedStatusMidModel
from .serializers import TyExistedStatusSerializer
# 其他 app 的views
from station.views_base import StationCommonView
from typhoon.views_base import TyGroupCommonView
from geo.views_base import GeoCommonView
# common
from util.enum import LayerTypeEnum


# Create your views here.


class LayerCheckView(BaseView, StationCommonView, TyGroupCommonView, GeoCommonView):
    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', None)
        forecast_dt_str: str = request.GET.get('forecast_dt')
        forecast_dt: datetime = arrow.get(forecast_dt_str).datetime
        timestamp_str: str = request.GET.get('timestamp', None)
        list_existed: List[int] = []
        if GeoCommonView().check_existed(ty_code, timestamp_str, forecast_dt):
            list_existed.append(LayerTypeEnum.GEO_RASTER_LAYER.value)
        if StationCommonView().check_existed(ty_code, timestamp_str, forecast_dt):
            list_existed.append(LayerTypeEnum.STATION_SURGE_ICON_LAYER.value)
        if TyGroupCommonView().check_existed(ty_code, timestamp_str, forecast_dt):
            list_existed.append(LayerTypeEnum.TYPHOON_GROUPPATH_LAYER.value)

        # status: TyExistedStatusMidModel = TyExistedStatusMidModel(
        #     GeoCommonView().check_existed(ty_code, timestamp_str, forecast_dt),
        #     StationCommonView().check_existed(ty_code, timestamp_str, forecast_dt),
        #     TyGroupCommonView().check_existed(ty_code, timestamp_str, forecast_dt))

        # self.json_data = TyExistedStatusSerializer(status, many=False).data
        self._status = 200
        return Response(list_existed, self._status)
