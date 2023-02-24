from typing import List, NewType, Dict
import datetime
import arrow
from celery import Celery
from TyphoonForecastSite.celery import app
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
from .models import CaseStatusModel, CaseInstanceModel
from .serializers import CaseStatusModelSerializer
from util.customer_exception import QueryNoneError
from util.log import log_in
from util.enum import ForecastAreaEnum
from others.my_celery import app


# Create your views here.
# CELERY = app


class TaskCreateView(BaseView):
    DeviationRadiusType = NewType('hours', int)
    MAX_WIND_RADIUS_DIFF: int = 50  # 大风半径增减值(可能出现负数-单位KM)
    MAX_RADIUS: int = 200
    MEMBERS_NUM: int = 160
    MEMBERS_NUM_LIST: List[int] = [5, 25, 45, 65, 85, 105, 125, 145]
    MIN_TIME_DIFF = datetime.timedelta(minutes=1)
    CELERY_TASK_NAME = 'surge_group_ty'
    # celery: Celery = Celery()
    celery: Celery = app

    # celery: Celery = app

    def get(self, request: Request) -> Response:
        my_task.delay('ceshi')
        pass

    def post(self, request: Request) -> Response:
        """
            调用 异步作业系统
            eg: post data:
                {'ty_code': '2109',
                'is_customer_ty': False,
                'customer_ty_cma_list': [
                            {'forecastDt': '2021-09-04T06:00:00.000Z',
                            'lat': 115.7,
                            'lon': 21.5,
                            'bp': 990,
                            'radius': 80},....],
                'max_wind_radius_diff': 0,
                'members_num': 145,
                'deviation_radius_list': [
                            {'hours': 24, 'radius': 60},....]}
        @param request:
        @return:
        """
        post_data: dict = request.data
        is_debug: bool = post_data.get('is_debug', True)
        is_customer_ty: bool = post_data.get('is_customer_ty')
        # todo :[-] 22-01-19 加入获取预报区域的判断
        area: int = post_data.get('forecast_area', ForecastAreaEnum.SCS)
        ty_customer_cma = {}
        if is_customer_ty:
            ty_customer_cma = {
                'ty_code': post_data.get('ty_code'),
                'customer_ty_cma_list': post_data.get('customer_ty_cma_list'),
                'forecast_area': area
            }
        max_wind_radius_diff: int = post_data.get('max_wind_radius_diff')
        members_num: int = post_data.get('members_num')
        # eg: [{'hours': 24, 'radius': 60}, {'hours': 48, 'radius': 100},
        #      {'hours': 72, 'radius': 120}, {'hours': 96, 'radius': 150}]}
        deviation_radius_list: List[Dict[str, int]] = post_data.get('deviation_radius_list')
        if self.verify(request) and self.to_idempotence(request):
            case: CaseInstanceModel = self.commit(request, is_debug, is_customer_ty=is_customer_ty,
                                                  ty_customer_cma=ty_customer_cma, forecast_area=area)
            self.json_data = {'ty_code': case.ty_code, 'timestamp': case.timestamp}
            self._status = 200
        elif not self.verify(request):
            self.json_data = '提交数据验证失败'
        elif not self.to_idempotence(request):
            self.json_data = '幂等性验证失败'
            pass
        return Response(self.json_data, self._status)

    def verify(self, request: Request, **kwargs) -> bool:
        """
            对于当前提交的 data 进行验证
        @param request:
        @param kwargs:
        @return:
        """
        is_verified: bool = False
        post_data: dict = request.data
        max_wind_radius_diff: int = post_data.get('max_wind_radius_diff')
        members_num: int = post_data.get('members_num')
        # eg: [{'hours': 24, 'radius': 60}, {'hours': 48, 'radius': 100},
        #      {'hours': 72, 'radius': 120}, {'hours': 96, 'radius': 150}]}
        deviation_radius_list: List[Dict[str, int]] = post_data.get('deviation_radius_list')
        if max_wind_radius_diff <= self.MAX_WIND_RADIUS_DIFF and members_num in self.MEMBERS_NUM_LIST:
            # 倒叙排列
            deviation_radius_list_sorted_desc = sorted(deviation_radius_list, key=lambda radius: radius.get('radius'),
                                                       reverse=True)
            if deviation_radius_list_sorted_desc[0].get('radius') <= self.MAX_RADIUS:
                # for temp_radius in deviation_radius_list:
                #     pass
                is_verified = True
        return is_verified

    def to_idempotence(self, request: Request, **kwargs) -> bool:
        """
            根据当前传入的参数进行幂等性判断
        :param request:
        :param kwargs:
        :return:
        """
        is_ok: bool = False
        post_data: dict = request.data
        ty_code: str = 'DEFAULT'
        max_wind_radius_diff: int = post_data.get('max_wind_radius_diff')
        members_num: int = post_data.get('members_num')
        # eg: [{'hours': 24, 'radius': 60}, {'hours': 48, 'radius': 100},
        #      {'hours': 72, 'radius': 120}, {'hours': 96, 'radius': 150}]}
        deviation_radius_list: List[Dict[str, int]] = post_data.get('deviation_radius_list')
        query = CaseInstanceModel.objects.filter(ty_code=ty_code, max_wind_radius_dif=max_wind_radius_diff,
                                                 member_num=members_num)
        if query is not None and len(query) > 0:
            query_json_field = query.first().json_field
            if query_json_field != deviation_radius_list:
                is_ok = True
            else:
                # 若存在 有相同 json_field 的，再判断创建的时间是否小于1min
                # 注意此处的 gmt_created 会包含时区，需要去掉时区信息
                gmt_created: datetime.datetime = query.first().gmt_modified
                gmt_created_arrow = arrow.get(gmt_created)
                utc_now_arrow = arrow.get(datetime.datetime.utcnow())
                if utc_now_arrow - gmt_created_arrow > self.MIN_TIME_DIFF:
                    is_ok = True
        elif query is not None and len(query) == 0:
            is_ok = True
        return is_ok

    def commit(self, request: Request, is_debug: bool = True, **kwargs) -> CaseInstanceModel:
        """
            - 21-12-01 提交后返回 task 的时间戳
        @param request:
        @param is_debug:
        @param kwargs:
        @return:
        """

        # step -1 : 将命名参数提取出来
        post_data: dict = request.data
        ty_code: str = post_data.get('ty_code')
        max_wind_radius_diff: int = post_data.get('max_wind_radius_diff')
        members_num: int = post_data.get('members_num')
        is_customer_ty: bool = kwargs.get('is_customer_ty')
        area: ForecastAreaEnum = kwargs.get('forecast_area')
        # {'ty_code': '2109',
        #  'customer_ty_cma_list':
        #      [{'forecastDt': '2021-09-04T06:00:00.000Z',
        #        'lat': 115.7,
        #        'lon': 21.5,
        #        'bp': 990},...]
        #  }
        ty_customer_cma: dict = kwargs.get('ty_customer_cma')
        ty_customer_list: List[dict] = ty_customer_cma.get('customer_ty_cma_list')
        # step -2 : 对 model 进行转换 convert
        # + 注意数组中的时间为 本地时区！！
        list_customer_cma: List[List[any]] = self._convert_ty_customer_cma(ty_customer_list) if is_customer_ty else []

        # eg: [{'hours': 24, 'radius': 60}, {'hours': 48, 'radius': 100},
        #      {'hours': 72, 'radius': 120}, {'hours': 96, 'radius': 150}]}
        deviation_radius_list: List[Dict[str, int]] = post_data.get('deviation_radius_list')
        # TODO:[-] 21-12-02 在后台接受post请求后生成时间戳
        timestamp: int = arrow.utcnow().int_timestamp
        commit_model: CaseInstanceModel = CaseInstanceModel.objects.create(ty_code=ty_code,
                                                                           timestamp=timestamp,
                                                                           gmt_commit=datetime.datetime.utcnow(),
                                                                           member_num=members_num,
                                                                           max_wind_radius_dif=max_wind_radius_diff,
                                                                           json_field=deviation_radius_list,
                                                                           area=area)
        # 21-09-20 customer_ty_cma_list -> forecastDt 需要转换为 2021071905 (local time)
        # 'customer_ty_cma_list': [
        #     {'forecastDt': '2021-09-04T06:00:00.000Z',
        #      'lat': 115.7,
        #      'lon': 21.5,
        #      'bp': 990,
        #      'radius': 80}, ....],
        # 提交至 celery
        params_obj = {'ty_code': ty_code, 'timestamp': timestamp, 'max_wind_radius_diff': max_wind_radius_diff,
                      'members_num': members_num,
                      'deviation_radius_list': deviation_radius_list, 'is_customer_ty': is_customer_ty,
                      'ty_customer_cma': list_customer_cma,
                      'forecast_area': area}
        log_in.info(f'接收到:ty_code:{ty_code}提交至celery')
        res = self.celery.send_task(self.CELERY_TASK_NAME, args=[params_obj, '123', 19], kwargs=params_obj)
        log_in.info(f'ty_code:{ty_code}提交至celery成功!')
        return commit_model
        # return True

    def _convert_ty_customer_cma(self, list_customer_cma: List[any]):
        """
            + 21-09-20 将 前台传入的 customer_cma_list 进行格式化
            -> :'customer_ty_cma_list': [
                    {'forecastDt': '2021-09-04T06:00:00.000Z',
                     'lat': 115.7,
                     'lon': 21.5,
                     'bp': 990,
                     'radius': 80}, ....],
            return : 'customer_ty_cma_list':
                      list[0] TY2112_2021090116_CMA_original 是具体的编号
                      List[1] ['2021082314', '2021082320'] 时间(切记返回的时区为本地时区切记！！)
                      list[2] ['125.3', '126.6'] 经度
                      list[3] ['31.3', '33.8']   维度
                      list[4] ['998', '998']     气压
                      list[5] ['15', '15']       暂时不用
        @param list_customer_cma:
        @return:
        """
        list_res: List[List[str]] = []
        list_dt_utc: List[str] = []
        list_dt_local: List[str] = []
        list_lat: List[str] = []
        list_lon: List[str] = []
        list_bp: List[str] = []
        # list_radius: List[str] = []
        # TODO:[-] 21-09-21 可以使用别的办法实现，不需要手动写
        for temp_customer_cma in list_customer_cma:
            # eg: temp_customer_cma : {'forecastDt': '2021-09-04T06:00:00.000Z', 'lat': 115.7, 'lon': 21.5, 'bp': 990}
            # step -1 : convert dt
            dt_str: str = temp_customer_cma.get('forecastDt')
            arrow_utc = arrow.get(dt_str)
            # TODO:[-] 21-10-22 此处发现一个会导致严重bug的问题，建议不使用 xx.to('local')
            # utc -> local
            arrow_local = arrow_utc.to('Asia/Shanghai')
            # arrow local -> format YYYYMMDDHH
            dt_local_str: str = arrow_local.format('YYYYMMDDHH')
            dt_utc_str: str = arrow_utc.format('YYYYMMDDHH')
            list_dt_local.append(dt_local_str)
            list_dt_utc.append(dt_utc_str)
            # list_dt.append(temp_customer_cma.get(''))
            # TODO:[-] 21-09-22 !注意此处要注意顺序，list[2] 为 lon 经度 ,list[3] 为 lat 纬度,切记!
            # step -2 : convert lon
            temp_lon: float = temp_customer_cma.get('lon')
            list_lon.append(str(temp_lon))
            # step -3 : convert lat
            temp_lat: float = temp_customer_cma.get('lat')
            list_lat.append(str(temp_lat))

            # step -4 : convert bp
            temp_bp: float = temp_customer_cma.get('bp')
            list_bp.append(str(temp_bp))
        list_res = ['', list_dt_local, list_lon, list_lat, list_bp, []]
        return list_res


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
