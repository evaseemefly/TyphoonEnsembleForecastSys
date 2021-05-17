from typing import List

from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.request import Request

# -- 本项目
from common.view_base import BaseView
from typhoon.views_base import TypGroupBaseView
from .models import TyphoonForecastDetailModel, TyphoonGroupPathModel, TyphoonForecastRealDataModel
from .mid_models import TyphoonComplexGroupRealDataMidModel
from .serializers import TyphoonForecastDetailSerializer, TyphoonGroupPathSerializer, TyphoonForecastRealDataSerializer, \
    TyphoonComplexGroupRealDataModelSerializer
from TyphoonForecastSite.settings import MY_PAGINATOR
from util.const import DEFAULT_NULL_KEY, UNLESS_TY_CODE

DEFAULT_PAGE_INDEX = MY_PAGINATOR.get('PAGE_INDEX')
DEFAULT_PAGE_COUNT = MY_PAGINATOR.get('PAGE_COUNT')


# Create your views here.

class TyDetailModelView(BaseView):
    """
        根据预报时间获取对应的 detailModel 列表
    """

    # _status = 500
    # json_data = None

    # @request_need_factors_wrapper(['ids'], 'GET')
    def get(self, request):
        """

        @param request:
        @return:
        """
        # 获取 ids
        forecast_dt = request.GET.get('forecast_dt', None)
        is_paged = request.GET.get('is_paged', False)
        page_index = request.GET.get('page_index', str(DEFAULT_PAGE_INDEX))
        page_count = DEFAULT_PAGE_COUNT

        query: List[TyphoonForecastDetailModel] = []
        if forecast_dt:
            query = TyphoonForecastDetailModel.objects.filter(gmt_start=forecast_dt)
            if is_paged:
                paginator = Paginator(query, page_count)
                contacts = paginator.get_page(page_index)
        try:
            self.json_data = TyphoonForecastDetailSerializer(contacts if is_paged else query, many=True).data
            self._status = 200
        except Exception as ex:
            self.json = ex.args

        return Response(self.json_data, status=self._status)


class TyGroupPathView(BaseView):
    """

    """

    def get(self, request):
        """
            根据 ty_id 获取 groupPath 列表
        @param request:
        @return:
        """
        # tyDetailModel id
        ty_id: int = int(request.GET.get('ty_id', str(DEFAULT_NULL_KEY)))
        # tyDetailModel code
        ty_code: str = request.GET.get('ty_code', UNLESS_TY_CODE)
        is_paged = bool(int(request.GET.get('is_paged', '0')))
        page_index = request.GET.get('page_index', str(DEFAULT_PAGE_INDEX))
        page_count = DEFAULT_PAGE_COUNT
        query: List[TyphoonGroupPathModel] = []
        if any([ty_id != DEFAULT_NULL_KEY, ty_code != UNLESS_TY_CODE]):
            query = TyphoonGroupPathModel.objects.filter(
                ty_id=ty_id) if ty_id != DEFAULT_NULL_KEY else TyphoonGroupPathModel.objects
            query = query.filter(ty_code=ty_code) if ty_code != UNLESS_TY_CODE else query
            if is_paged:
                paginator = Paginator(query, page_count)
                contacts = paginator.get_page(page_index)
            try:
                self.json_data = TyphoonGroupPathSerializer(contacts if is_paged else query, many=True).data
                self._status = 200
            except Exception as ex:
                self.json = ex.args
        return Response(self.json_data, status=self._status)


class TyRealDataView(BaseView):
    def get(self, request: Request) -> Response:
        """
            根据 group_ id 获取 对应的台风实时数据
        @param request:
        @return:
        """
        groupd_id: int = int(request.GET.get('group_id', str(DEFAULT_NULL_KEY)))
        is_paged = bool(int(request.GET.get('is_paged', '0')))
        page_index = request.GET.get('page_index', str(DEFAULT_PAGE_INDEX))
        page_count = DEFAULT_PAGE_COUNT
        query: List[TyphoonGroupPathModel] = []
        if groupd_id != DEFAULT_NULL_KEY:
            query = TyphoonForecastRealDataModel.objects.filter(
                gp_id=groupd_id) if groupd_id != DEFAULT_NULL_KEY else TyphoonForecastRealDataModel.objects

            if is_paged:
                paginator = Paginator(query, page_count)
                contacts = paginator.get_page(page_index)
            try:
                self.json_data = TyphoonForecastRealDataSerializer(contacts if is_paged else query, many=True).data
                self._status = 200
            except Exception as ex:
                self.json = ex.args
        return Response(self.json_data, status=self._status)


class TyComplexGroupRealDatasetView(BaseView):
    def get(self, request: Request) -> Response:
        """
            + 21-04-19
            根据 ty_id 获取 group 集合 + realdata list 的这种组合
        @param reuqest:
        @return:
        """
        ty_id: int = int(request.GET.get('ty_id', str(DEFAULT_NULL_KEY)))
        is_paged = bool(int(request.GET.get('is_paged', '0')))
        page_index = request.GET.get('page_index', str(DEFAULT_PAGE_INDEX))
        page_count = DEFAULT_PAGE_COUNT
        list_groupComplex: List[TyComplexGroupRealDatasetView] = []
        if ty_id != DEFAULT_NULL_KEY:
            query = TyphoonGroupPathModel.objects.filter(
                ty_id=ty_id)
            if is_paged:
                paginator = Paginator(query, page_count)
                contacts = paginator.get_page(page_index)
            try:
                for group_temp in contacts if is_paged else query:
                    list_realdata: List[TyphoonForecastRealDataModel] = []
                    group_id: int = group_temp.id
                    # 根据当前的 group_id 获取 ty_realdata
                    list_realdata = TyphoonForecastRealDataModel.objects.filter(gp_id=group_id)
                    groupComplex_temp: TyphoonComplexGroupRealDataMidModel = TyphoonComplexGroupRealDataMidModel(
                        ty_id=group_temp.ty_id, ty_code=group_temp.ty_code, area=group_temp.area,
                        timestamp=group_temp.timestamp, ty_path_type=group_temp.ty_path_type,
                        ty_path_marking=group_temp.ty_path_marking, bp=group_temp.bp,
                        is_bp_increase=group_temp.is_bp_increase, list_realdata=list_realdata)
                    list_groupComplex.append(groupComplex_temp)
                self.json_data = TyphoonComplexGroupRealDataModelSerializer(list_groupComplex, many=True).data
                self._status = 200
            except Exception as ex:
                # ERROR:
                # Got AttributeError when attempting to get a value for field `ty_id` on serializer `TyphoonComplexGroupRealDataModelSerializer`.
                # The serializer field might be named incorrectly and not match any attribute or key on the `list` instance.
                # Original exception text was: 'list' object has no attribute 'ty_id'.
                self.json = ex.args
        return Response(self.json_data, status=self._status)


class TyDataRangeView(TypGroupBaseView):
    def get(self, request: Request) -> Response:
        """

        @param request:
        @return:
        """
        ty_id: int = int(request.GET.get('ty_id', str(DEFAULT_NULL_KEY)))
        ty_code: str = request.GET.get('ty_code', UNLESS_TY_CODE)
        timestamp_str: str = request.GET.get('timestamp', None)
        query = self.getCenterGroupPath(ty_code=ty_code, timestamp=timestamp_str)
        return Response(self.json_data, status=self._status)
