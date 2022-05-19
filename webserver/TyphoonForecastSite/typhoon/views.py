from typing import List
import requests
import http.client
from lxml import etree
# import datetime
from datetime import timedelta, datetime
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.db.models import Max, Min
from rest_framework.response import Response
from rest_framework.request import Request

# --- 第三方库
import arrow

# -- 本项目
from common.view_base import BaseView
from typhoon.views_base import TyGroupBaseView, TySpiderBaseView
from .models import TyphoonForecastDetailModel, TyphoonGroupPathModel, TyphoonForecastRealDataModel
from .mid_models import TyphoonComplexGroupRealDataMidModel, TyphoonGroupDistMidModel, TyphoonContainsCodeAndStMidModel, \
    TyphoonGroupRealDataDistMidModel, TyphoonComplexGroupDictMidModel, TyDetailMidModel, TyPathMidModel
from .serializers import TyphoonForecastDetailSerializer, TyphoonGroupPathSerializer, TyphoonForecastRealDataSerializer, \
    TyphoonComplexGroupRealDataModelSerializer, TyphoonDistGroupPathMidSerializer, TyphoonContainsCodeAndStSerializer, \
    TyphoonComplexGroupRealDataNewModelSerializer, TyphoonComplexGroupDictMidSerializer, TyRealDataMidSerializer, \
    TyPathMidSerializer
from TyphoonForecastSite.settings import MY_PAGINATOR, PROJ_VERSIONS
from util.const import DEFAULT_NULL_KEY, UNLESS_TY_CODE, DEFAULT_TIMTSTAMP_STR, DEFAULT_CODE

DEFAULT_PAGE_INDEX = MY_PAGINATOR.get('PAGE_INDEX')
DEFAULT_PAGE_COUNT = MY_PAGINATOR.get('PAGE_COUNT')


# Create your views here.
class TyTestView(BaseView):
    def get(self, request):
        self.json_data = PROJ_VERSIONS
        self._status = 200
        return Response(self.json_data, status=self._status)


class JsonTestView(BaseView):
    def get(self, request):
        json = {'tycode': '1234', 'timestamp': '123456'}
        self.json_data = json
        self._status = 200
        return Response(self.json_data, status=self._status)


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
    def get_old(self, request: Request) -> Response:
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
                self.json_data = ex.args
        return Response(self.json_data, status=self._status)

    def get(self, request: Request) -> Response:
        ty_id: int = int(request.GET.get('ty_id', str(DEFAULT_NULL_KEY)))
        if ty_id != DEFAULT_NULL_KEY:
            try:
                # step-1 : 根据 ty_id 拼接两张表
                query = TyphoonGroupPathModel.objects.filter(
                    ty_id=ty_id).extra(
                    select={'timestamp': 'typhoon_forecast_grouppath.timestamp',
                            'lat': 'typhoon_forecast_realdata.lat',
                            'lon': 'typhoon_forecast_realdata.lon',
                            'realdata_bp': 'typhoon_forecast_realdata.bp',
                            'group_bp': 'typhoon_forecast_grouppath.bp',
                            'gale_radius': 'typhoon_forecast_realdata.gale_radius',
                            'ty_path_type': 'typhoon_forecast_grouppath.ty_path_type',
                            'ty_path_marking': 'typhoon_forecast_grouppath.ty_path_marking',
                            'is_bp_increase': 'typhoon_forecast_grouppath.is_bp_increase',
                            'forecast_dt': 'typhoon_forecast_realdata.forecast_dt',
                            'gp_id': 'typhoon_forecast_grouppath.id'},
                    tables=['typhoon_forecast_realdata', 'typhoon_forecast_grouppath'],
                    where=['typhoon_forecast_realdata.gp_id=typhoon_forecast_grouppath.id'])
                # step-2 : 将不同的 gp_id 抽取出来放到不同的数组中
                query_list = list(query)
                list_group_dict: dict = {}
                # { gp_id:'',realdata_list:[xx]}
                list_group: List[any] = []
                for temp in query_list:
                    # 方式 2-1
                    if temp.gp_id not in list_group_dict:
                        list_group_dict[temp.gp_id] = []
                    list_group_dict[temp.gp_id].append(temp)
                for item in list_group_dict:
                    # item['gp_id'] = item
                    first_realdata = list_group_dict[item][0]
                    item_dist_group: TyphoonComplexGroupDictMidModel = TyphoonComplexGroupDictMidModel(item,
                                                                                                       first_realdata.ty_path_type,
                                                                                                       first_realdata.ty_path_marking,
                                                                                                       first_realdata.bp,
                                                                                                       first_realdata.is_bp_increase,
                                                                                                       list_group_dict[
                                                                                                           item])
                    list_group.append(item_dist_group)
                    # pass

                    # 方式 2-2
                #     if len(list_group) > 0:
                #         for temp_dict in list_group:
                #             if temp_dict['gp_id'] and temp_dict['gp_id'] == temp.gp_id:
                #                 temp_dict['real_data'].append(temp)
                #             else:
                #                 list_group.append({'gp_id': temp.gp_id, 'real_data': [temp]})
                #     else:
                #         list_group.append({'gp_id': temp.gp_id, 'real_data': [temp]})
                # json_data = TyphoonComplexGroupRealDataNewModelSerializer(query, many=True).data
                # json_data=
                json_data = TyphoonComplexGroupDictMidSerializer(list_group, many=True).data
                self.json_data = json_data
                self._status = 200
            except Exception as ex:
                self.json_data = ex.args
        return Response(self.json_data, status=self._status)


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
            gmt_start__gte=year_start_arrow.datetime, gmt_end__lte=year_end_arrow.datetime, is_del=False).exclude(
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
                                                            gmt_created=temp_gp_model.gmt_created,
                                                            start=start.get('start'),
                                                            end=end.get('end'))
                        ty_group_dist_list.append(temp_mid)
        if len(ty_group_dist_list) > 0:
            json_data = TyphoonDistGroupPathMidSerializer(ty_group_dist_list, many=True)
            self.json_data = json_data.data
            self._status = 200
        return Response(self.json_data, self._status)


class TyTargetCase(BaseView):
    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', None)
        timestamp: str = request.GET.get('timestamp', None)
        if any([ty_code, timestamp]) is not None:
            query: QuerySet = TyphoonForecastDetailModel.objects.filter(code=ty_code, timestamp=timestamp)
            if len(query) > 0:
                target_ty: TyphoonForecastDetailModel = query.first()
                json_data = TyphoonForecastDetailSerializer(target_ty).data
                self.json_data = json_data
                self._status = 200
        return Response(self.json_data, self._status)


class TyCMAView(BaseView):
    """
        + 22-04-02 获取中央气象台的台风路径信息
    """

    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', DEFAULT_CODE)
        cma_res: List[{}] = []
        if ty_code != DEFAULT_CODE:
            cma_res = self._get_typath_cma(ty_code)
        pass

    def _get_typath_cma(self, tyno: str, **kwargs):
        """
            TODO:[-] 此处返回值有可能是None，对于不存在的台风编号，则返回空？
                    抓取台风
                 +  21-09-21 此处加入了 根据 用户自定义的台风 生成对应台风路径文件 及 其他 步骤
                 - 21-09-21 此方法是否就是 生成 _cma_original 文件以及返回 list[8] 数组
                 -          生成的 _cma_original 文件只是留存，之后不会再使用了 !
            返回值
                    [filename,
                    tcma, 时间
                    loncma, 对应经度
                    latcma, 对应纬度
                    pcma, 气压
                    spdcma, 最大风速
                    id, 台风编号
                    tyname] 台风名称(若非台风则为None)
                eg:
                    ['TYtd03_2021071606_CMA_original',
                    ['2021070805', '2021070811', '2021070817'],
                    ['106.3', '104.7', '103.2'],
                    ['19.5', '19.7', '19.9'],
                    ['1000', '1002', '1004'],
                    ['15', '12', '10'],
                    'TD03',
                    None]
                    ['TYtd04_2021071901_CMA_original',  - filename
                    ['2021071905', '2021071917',        - tcma
                     '2021072005','2021072017',
                      '2021072105', '2021072117',
                      '2021072205'],
                      ['113.2',  '113.0',              - loncma
                      '113.1','112.9',
                      '112.3','111.6',
                      '111.1'],
                       ['20.8', '21.0',               - latcma
                       '21.3', '21.7',
                       '21.9', '21.9',
                       '21.8'],
                       ['1000', '998',              - pcma
                       '990', '985',
                       '995', '998', '1000'],
                       ['15', '18',                - spdcma
                       '23', '25',
                        '20', '18',
                        '15'],
                        'TD04',                   - id
                        None]                     - tyname
        :param tyno:  台风编号
        :return:[ ['2021070805', '2021070811', '2021070817'], ['106.3', '104.7', '103.2'], ['19.5', '19.7', '19.9'], ['1000', '1002', '1004'], ['15', '12', '10'], 'TD03', None]
        """
        import os
        url = "http://www.nmc.cn/publish/typhoon/message.html"
        try:
            page = requests.get(url, timeout=60)
        except:
            print("CMA: internet problem!")
            return None
        # page="./test.html"

        # html = etree.parse(page, etree.HTMLParser())
        selector = etree.HTML(page.text)
        # selector = etree.HTML(etree.tostring(html))
        infomation = selector.xpath('/html/body/div[2]/div/div[2]/div[1]/div[2]/div/text()')
        # if not infomation==[]:#生成提示为乱码，目前认为有提示即不是最新结果
        #    print(infomation)
        #    sys.exit(0)
        times = selector.xpath('//*[@id="mylistcarousel"]/li/p/text()')  # 获取tab时间列表
        head = "http://www.nmc.cn/f/rest/getContent?dataId=SEVP_NMC_TCMO_SFER_ETCT_ACHN_L88_P9_"
        # n=len(ids) #查找台风数
        # print(times)
        outcma = None
        kk = 0
        if times == []:  # 第一份
            forecast = selector.xpath('//*[@id="text"]/p/text()')
            info = self._parse_first(forecast)
            # print(info)
            if info == None:
                pass
            else:
                id = info[-1]
                print(id)
                spdcma = info[-2]
                pcma = info[-3]
                latcma = info[-4]
                loncma = info[-5]
                tcma = info[-6]
                tyname = info[-7]
                year = datetime.now().year
                month = datetime.now().month
                day = datetime.now().day
                hour = datetime.now().hour
                if month < 10:
                    smonth = '0' + str(month)
                else:
                    smonth = str(month)
                if day < 10:
                    sday = '0' + str(day)
                else:
                    sday = str(day)
                if hour < 10:
                    shrs = '0' + str(hour)
                else:
                    shrs = str(hour)
                if id == tyno:
                    outcma = [tcma, loncma, latcma, pcma, spdcma, id, tyname]

        else:
            for item in times:
                string = item.replace(" ", "").replace(":", "").replace("/", "") + "00000"
                url1 = head + string
                page1 = requests.get(url1, timeout=60)
                contents = page1.text.replace("<br>", "").split("\n")
                # content=selector.xpath('/html/body/p/text()')
                info = self._parse_info(contents, item)
                # file="./"+string+".txt"
                if info == None:
                    pass
                else:
                    id = info[-1]
                    # print(id)

                    spdcma = info[-2]
                    pcma = info[-3]
                    latcma = info[-4]
                    loncma = info[-5]
                    tcma = info[-6]
                    tyname = info[-7]

                    year = datetime.now().year
                    month = datetime.now().month
                    day = datetime.now().day
                    hour = datetime.now().hour
                    if month < 10:
                        smonth = '0' + str(month)
                    else:
                        smonth = str(month)
                    if day < 10:
                        sday = '0' + str(day)
                    else:
                        sday = str(day)
                    if hour < 10:
                        shrs = '0' + str(hour)
                    else:
                        shrs = str(hour)

                    if id == tyno:
                        outcma = [tcma, loncma, latcma, pcma, spdcma, id, tyname]
                        kk = kk + 1
                        if kk == 1:
                            break  # 保证找到一条最新的预报结果后退出
        return outcma

    def _parse_first(self, list):
        '''

        :param list:
        :return:
        '''
        result = []
        lon_all = []
        lat_all = []
        pre_all = []
        speed_all = []
        tcma = []
        time_str = list[1].split()[2]
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day
        if day < 10:
            day = "0" + str(day)
        else:
            day = str(day)
        if day >= time_str[0:2]:
            time = str(year) + "/" + str(month) + "/" + time_str[0:2] + " " + time_str[2:4] + ":" + time_str[4:] + ":00"
        else:
            month = str(month - 1)
            if month == 0:
                year = str(year - 1)
                month = 12
            else:
                # month = str(int(month) - 1)
                pass
            time = str(year) + "/" + str(month) + "/" + time_str[0:2] + " " + time_str[2:4] + ":" + time_str[4:] + ":00"

        if list[3].split()[0] == "TD" and list[3].split()[1].isnumeric():
            id = list[3].split()[0] + list[3].split()[1]
            tyname = None
        else:
            id = list[3].split()[2]
            tyname = list[3].split()[1]

        for line in list:

            if line[:5] == " 00HR":

                time1 = datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S') + timedelta(hours=8)
                if time1.month < 10:
                    month_str = "0" + str(time1.month)
                else:
                    month_str = str(time1.month)
                if time1.day < 10:
                    day_str = "0" + str(time1.day)
                else:
                    day_str = str(time1.day)
                if time1.hour < 10:
                    hr_str = "0" + str(time1.hour)
                else:
                    hr_str = str(time1.hour)
                time_num_c = month_str + day_str + hr_str

                if line.split(" ")[2][-1] == "N":
                    lat = float(line.split(" ")[2][:-1])
                else:
                    lat = float(line.split(" ")[2][:-1]) * -1
                if line.split(" ")[3][-1] == "E":
                    lon = float(line.split(" ")[3][:-1])
                else:
                    lon = float(line.split(" ")[3][:-1]) * -1
                pa = line.split(" ")[4].split("H")[0]
                v = line.split(" ")[5].split("M")[0]
                result.append(" " + time_num_c + " " + str(lon) + " " + str(lat) + " " + pa + " " + v)
                tcma.append(str(year) + time_num_c)
                lon_all.append(str(lon))
                lat_all.append(str(lat))
                pre_all.append(pa)
                speed_all.append(v)

            if line[:3] == " P+":
                hr = line.split(" ")[1][2:5]
                if hr[-1] == 'H':
                    hr = hr[:-1]
                if hr[0] == "0":
                    hr = hr[1]
                time1 = datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S') + timedelta(
                    hours=8) + timedelta(hours=int(hr))
                if time1.month < 10:
                    month_str = "0" + str(time1.month)
                else:
                    month_str = str(time1.month)
                if time1.day < 10:
                    day_str = "0" + str(time1.day)
                else:
                    day_str = str(time1.day)
                if time1.hour < 10:
                    hr_str = "0" + str(time1.hour)
                else:
                    hr_str = str(time1.hour)
                time_num_c = month_str + day_str + hr_str
                if line.split(" ")[2][-1] == "N":
                    lat = float(line.split(" ")[2][:-1])
                else:
                    lat = float(line.split(" ")[2][:-1]) * -1
                if line.split(" ")[3][-1] == "E":
                    lon = float(line.split(" ")[3][:-1])
                else:
                    lon = float(line.split(" ")[3][:-1]) * -1
                pa = line.split(" ")[4].split("H")[0]
                v = line.split(" ")[5].split("M")[0]
                result.append(" " + time_num_c + " " + str(lon) + " " + str(lat) + " " + pa + " " + v)
                tcma.append(str(year) + time_num_c)
                lon_all.append(str(lon))
                lat_all.append(str(lat))
                pre_all.append(pa)
                speed_all.append(v)
            else:
                continue

        if result == []:
            return None
        else:
            result.append(tyname)
            result.append(tcma)
            result.append(lon_all)
            result.append(lat_all)
            result.append(pre_all)
            result.append(speed_all)
            result.append(id)
            return result

    def _parse_info(self, list, time_issu):
        result = []
        lon_all = []
        lat_all = []
        pre_all = []
        speed_all = []
        tcma = []
        pflag = 0
        for i in range(len(list)):
            if list[i][:2] == 'P+':
                pflag = 1
                continue

        if list[3] == "SUBJECTIVE FORECAST" and pflag == 1:
            time_str = list[2].split()[2]
            year = time_issu.split()[0].split("/")[0]
            month = time_issu.split()[0].split("/")[1]
            day = time_issu.split()[0].split("/")[2]
            if day >= time_str[0:2]:
                time = year + "/" + month + "/" + time_str[0:2] + " " + time_str[2:4] + ":" + time_str[4:] + ":00"
            else:
                if month[0] == 0:
                    month = "0" + str(int(month[1]) - 1)
                    if month == "00":
                        year = str(int(year) - 1)
                        month = "12"
                else:
                    month = str(int(month) - 1)
                time = year + "/" + month + "/" + time_str[0:2] + " " + time_str[2:4] + ":" + time_str[4:] + ":00"

            if list[4].split()[0] == "TD" and list[4].split()[1].isnumeric():
                id = list[4].split()[0] + list[4].split()[1]
                tyname = None
            else:
                id = list[4].split()[2]
                tyname = list[4].split()[1]

            for line in list:

                if line[:4] == "00HR":

                    time1 = datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S') + timedelta(hours=8)
                    if time1.month < 10:
                        month_str = "0" + str(time1.month)
                    else:
                        month_str = str(time1.month)
                    if time1.day < 10:
                        day_str = "0" + str(time1.day)
                    else:
                        day_str = str(time1.day)
                    if time1.hour < 10:
                        hr_str = "0" + str(time1.hour)
                    else:
                        hr_str = str(time1.hour)
                    time_num_c = month_str + day_str + hr_str

                    if line.split(" ")[1][-1] == "N":
                        lat = float(line.split(" ")[1][:-1])
                    else:
                        lat = float(line.split(" ")[1][:-1]) * -1
                    if line.split(" ")[2][-1] == "E":
                        lon = float(line.split(" ")[2][:-1])
                    else:
                        lon = float(line.split(" ")[2][:-1]) * -1
                    pa = line.split(" ")[3].split("H")[0]
                    v = line.split(" ")[4].split("M")[0]
                    result.append(" " + time_num_c + " " + str(lon) + " " + str(lat) + " " + pa + " " + v)
                    tcma.append(str(year) + time_num_c)
                    lon_all.append(str(lon))
                    lat_all.append(str(lat))
                    pre_all.append(pa)
                    speed_all.append(v)

                if line[:2] == "P+":
                    hr = line.split(" ")[0][2:5]
                    if hr[-1] == 'H':
                        hr = hr[:-1]
                    if hr[0] == "0":
                        hr = hr[1]
                    time1 = datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S') + timedelta(
                        hours=8) + timedelta(hours=int(hr))
                    if time1.month < 10:
                        month_str = "0" + str(time1.month)
                    else:
                        month_str = str(time1.month)
                    if time1.day < 10:
                        day_str = "0" + str(time1.day)
                    else:
                        day_str = str(time1.day)
                    if time1.hour < 10:
                        hr_str = "0" + str(time1.hour)
                    else:
                        hr_str = str(time1.hour)
                    time_num_c = month_str + day_str + hr_str
                    if line.split(" ")[1][-1] == "N":
                        lat = float(line.split(" ")[1][:-1])
                    else:
                        lat = float(line.split(" ")[1][:-1]) * -1
                    if line.split(" ")[2][-1] == "E":
                        lon = float(line.split(" ")[2][:-1])
                    else:
                        lon = float(line.split(" ")[2][:-1]) * -1
                    pa = line.split(" ")[3].split("H")[0]
                    v = line.split(" ")[4].split("M")[0]
                    result.append(" " + time_num_c + " " + str(lon) + " " + str(lat) + " " + pa + " " + v)
                    tcma.append(str(year) + time_num_c)
                    lon_all.append(str(lon))
                    lat_all.append(str(lat))
                    pre_all.append(pa)
                    speed_all.append(v)
                else:
                    continue
            if result == []:
                return None
            else:
                result.append(tyname)
                result.append(tcma)
                result.append(lon_all)
                result.append(lat_all)
                result.append(pre_all)
                result.append(speed_all)
                result.append(id)
                return result
        else:
            return None


class TySpiderCMAView(TySpiderBaseView):
    """
        根据传入的台风编号爬取对应的台风并返回
    """

    def get(self, request: Request) -> Response:
        ty_code: str = request.GET.get('ty_code', None)
        ty_detail: TyDetailMidModel = self.spider_check_ty_exist(ty_code)
        ty_cma_data: TyPathMidModel = None
        if ty_detail is None:
            self.json_data = '不存在指定台风'
            self._status = 200
        else:
            try:
                ty_cma_data = self.spider_get_ty_path(ty_detail.id, ty_detail.ty_code, ty_detail.ty_name_en)
                if ty_cma_data is not None:
                    self.json_data = TyPathMidSerializer(ty_cma_data).data
                    self._status = 200
            except Exception as ex:
                self.json_data = f'爬取{ty_detail.ty_code}时出现异常'
        return Response(self.json_data, status=self._status)
        pass
