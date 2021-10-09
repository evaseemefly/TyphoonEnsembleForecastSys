from typing import List

from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.db.models import Max, Min
from rest_framework.response import Response
from rest_framework.request import Request

# --- 第三方库
import arrow

# -- 本项目
from common.view_base import BaseView
from typhoon.views_base import TyGroupBaseView
from .models import TyphoonForecastDetailModel, TyphoonGroupPathModel, TyphoonForecastRealDataModel
from .mid_models import TyphoonComplexGroupRealDataMidModel, TyphoonGroupDistMidModel, TyphoonContainsCodeAndStMidModel
from .serializers import TyphoonForecastDetailSerializer, TyphoonGroupPathSerializer, TyphoonForecastRealDataSerializer, \
    TyphoonComplexGroupRealDataModelSerializer, TyphoonDistGroupPathMidSerializer, TyphoonContainsCodeAndStSerializer
from TyphoonForecastSite.settings import MY_PAGINATOR
from util.const import DEFAULT_NULL_KEY, UNLESS_TY_CODE, DEFAULT_TIMTSTAMP_STR

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
                # TODO:[-] 21-10-09 此处尝试减少连接 db 的次数
                # 一下部分考虑采用 先 filter 在 extra 的方法查询
                # sql ：
                # SELECT
                # rd.lat, rd.lon, rd.bp, rd.gale_radius, gp.
                # `timestamp`, gp.ty_path_type, gp.ty_path_marking, gp.is_bp_increase
                # FROM
                # typhoon_forecast_realdata as rd, typhoon_forecast_grouppath as gp
                # WHERE
                # rd.gp_id = gp.id
                # AND
                # gp.ty_id = 27
                for group_temp in contacts if is_paged else query.iterator():
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
                json_data = TyphoonComplexGroupRealDataModelSerializer(list_groupComplex, many=True).data
                # ty_qs = TyphoonComplexGroupRealDataModelSerializer.setup_eager_loading(list_groupComplex)
                # json_data = TyphoonComplexGroupRealDataModelSerializer(ty_qs, many=True).data
                self.json_data = json_data
                self._status = 200
            except Exception as ex:
                # ERROR:
                # Got AttributeError when attempting to get a value for field `ty_id` on serializer `TyphoonComplexGroupRealDataModelSerializer`.
                # The serializer field might be named incorrectly and not match any attribute or key on the `list` instance.
                # Original exception text was: 'list' object has no attribute 'ty_id'.
                self.json = ex.args
        return Response(self.json_data, status=self._status)

    def get_new(self, request: Request) -> Response:
        ty_id: int = int(request.GET.get('ty_id', str(DEFAULT_NULL_KEY)))
        is_paged = bool(int(request.GET.get('is_paged', '0')))
        page_index = request.GET.get('page_index', str(DEFAULT_PAGE_INDEX))
        page_count = DEFAULT_PAGE_COUNT
        list_groupComplex: List[TyComplexGroupRealDatasetView] = []
        if ty_id != DEFAULT_NULL_KEY:
            query = TyphoonGroupPathModel.objects.filter(
                ty_id=ty_id)


class TyDataRangeView(TyGroupBaseView):
    """

    """

    def get(self, request: Request) -> Response:
        """
            获取对应的 tyGroup 的时间范围
        @param request:
        @return:
        """
        ty_id: int = int(request.GET.get('ty_id', str(DEFAULT_NULL_KEY)))
        ty_code: str = request.GET.get('ty_code', None)
        timestamp_str: str = request.GET.get('timestamp', None)
        dt_range: [] = []
        if all([ty_code, timestamp_str]) and not 'DEFAULT' in [ty_code, timestamp_str]:
            query = self.getCenterGroupPath(ty_code=ty_code, timestamp=timestamp_str)
            dt_range = self.getCenterPathDateRange((query.first()))
        else:
            dt_range = self.getDefaultDateRange()
        self.json_data = dt_range
        self._status = 200
        return Response(self.json_data, status=self._status)


class TyGroupDateDistView(TyGroupBaseView):
    def get(self, request: Request) -> Response:
        """
            获取对应的 tyGroup 的时间列表(相当于知道了时间间隔)
        @param request:
        @return:
        """
        ty_id: int = int(request.GET.get('ty_id', str(DEFAULT_NULL_KEY)))
        ty_code: str = request.GET.get('ty_code', None)
        timestamp_str: str = request.GET.get('timestamp', None)
        list_dt_dist: [] = []
        if all([ty_code, timestamp_str]):
            try:
                query = self.getCenterGroupPath(ty_code=ty_code, timestamp=timestamp_str)
                list_dt_dist = self.getDateDist(query.first())
                self.json_data = list_dt_dist
                self._status = 200
            except Exception as e:
                print(e.args)

        return Response(self.json_data, status=self._status)


class TyList(BaseView):
    """
        根据传入的参数获取对应台风列表
    """

    def get(self, request: Request) -> Response:
        year = request.GET.get('year', None)
        # year = '2021'
        year_start_arrow: arrow.Arrow = arrow.Arrow(int(year), 1, 1)
        year_end_arrow: arrow.Arrow = arrow.Arrow(int(year), 12, 31, 23, 59)
        ty_match_query: List[TyphoonForecastDetailModel] = TyphoonForecastDetailModel.objects.filter(
            gmt_start__gte=year_start_arrow.datetime, gmt_end__lte=year_end_arrow.datetime).exclude(
            timestamp=DEFAULT_TIMTSTAMP_STR)
        # TODO:[-] 21-09-12 只根据 code 进行去重，不需要根据 时间戳去重
        ty_match_mids: List[dict] = ty_match_query.values('code').distinct()
        # + 21-07-27 因为返回的直接是字典数组所以不必多此一举做序列化了
        # ty_match_mid_list = [
        #     TyphoonContainsCodeAndStMidModel(ty_code=temp.get('code'), timestamp_str=temp.get('timestamp')) for
        #     temp in ty_match_mids]
        try:
            # self.json_data = TyphoonForecastDetailSerializer(ty_match_list, many=True).data
            self.json_data = ty_match_mids
            self._status = 200
        except Exception as ex:
            self.json_data = ex.args
        return Response(self.json_data, self._status)
        pass


class TyCaseList(BaseView):
    '''
        + 21-07-25
        desc: 根据 ty_code 获取该台风对应的全部 case : ty_code_tmestamp
    '''

    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', None)
        ty_group_dist_list: List[TyphoonGroupDistMidModel] = []
        if ty_code is not None:
            # ty_group_dist_list = TyphoonGroupPathModel.objects.filter(ty_code=ty_code).distinct('ty_id').all()
            # ERROR1:
            # ty_group_dist_list = TyphoonGroupPathModel.objects.filter(ty_code=ty_code).values('timestamp',
            #                                                                                   'ty_code',
            #                                                                                   'gmt_created').distinct(
            #     'timestamp')
            # 方式1:
            # [{'ty_code':'xxx'}]
            ty_dist_ty_timestamp: List[dict] = list(
                TyphoonGroupPathModel.objects.filter(ty_code=ty_code).values('timestamp').distinct())

            # 方式2:
            # ty_group_dist_list = TyphoonGroupPathModel.objects.raw(
            #     f'SELECT * FROM `typhoon_forecast_grouppath` as gp WHERE gp.ty_code="{ty_code}" GROUP BY gp.`timestamp` ORDER BY gp.`timestamp` DESC')[
            #     0]
            # 查找到不同的 timstamp 后，再继续找到该 timestmap 对应的 group_info 的 gmt_created
            if len(ty_dist_ty_timestamp) > 0:
                for temp in ty_dist_ty_timestamp:
                    temp_ts = temp.get('timestamp')
                    # step-1: 根据 ty_code 与 ts 查找 group 的基础信息
                    temp_gp_model: TyphoonGroupPathModel = TyphoonGroupPathModel.objects.filter(ty_code=ty_code,
                                                                                                timestamp=temp_ts).order_by(
                        'gmt_created').first()
                    # step-2: 根据 group_id 找到 tb:ty_forecast_realdata 的起止时间范围
                    ty_realdata_list: QuerySet = TyphoonForecastRealDataModel.objects.filter(
                        ty_id=temp_gp_model.ty_id, gp_id=temp_gp_model.id).order_by('forecast_dt')
                    if len(ty_realdata_list) > 0:
                        start: dict = ty_realdata_list.aggregate(start=Min('forecast_dt'))
                        end: dict = ty_realdata_list.aggregate(end=Max('forecast_dt'))
                    temp_mid = TyphoonGroupDistMidModel(ty_id=temp_gp_model.ty_id, ty_code=temp_gp_model.ty_code,
                                                        timestamp=temp_gp_model.timestamp,
                                                        gmt_created=temp_gp_model.gmt_created, start=start.get('start'),
                                                        end=end.get('end'))
                    ty_group_dist_list.append(temp_mid)
        if len(ty_group_dist_list) > 0:
            json_data = TyphoonDistGroupPathMidSerializer(ty_group_dist_list, many=True)
            self.json_data = json_data.data
            self._status = 200
        return Response(self.json_data, self._status)
