from abc import ABCMeta, abstractclassmethod, abstractmethod, ABC
import datetime
import time
import requests
from lxml import etree
import subprocess
import arrow

#
import os
import numpy as np
from math import *
from scipy import interpolate
from netCDF4 import Dataset
from geographiclib.geodesic import Geodesic
# TODO:[-] 建议以后均使用 pathlib 模块来进行 path相关的操作
import pathlib
from datetime import timedelta, datetime

from typing import List
from model.models import CaseStatus
from util.customer_decorators import log_count_time, store_job_rate
from util.log import Loggings, log_in
from common.enum import JobInstanceEnum, TaskStateEnum, ForecastAreaEnum, get_area_dp_file
from util.customer_excption import CalculateTimeOutError
from util.customer_decorators import except_log
from conf.settings import TEST_ENV_SETTINGS, JOB_SETTINGS, MODIFY_CHMOD_PATH, MODIFY_CHMOD_FILENAME, TIME_ZONE
from common.common_dict import get_forecast_area_range, get_forecast_area_latlngs

SHARED_PATH = TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR')
MAX_TIME_INTERVAL: int = JOB_SETTINGS.get('MAX_TIME_INTERVAL')


class IBaseJob(metaclass=ABCMeta):
    """
        基础 job 抽象类

    """

    def __init__(self, ty_code: str, timestamp: str = None):
        """
            实例化时就获取当前的时间戳
        @param ty_code:
        @param timestamp:
        """
        self.ty_code: str = ty_code
        self.timestamp: int = int(timestamp) if timestamp else arrow.utcnow().int_timestamp
        self.list_cmd = []
        self.parent_path = SHARED_PATH

    @property
    def timestamp_str(self) -> str:
        """
            时间戳 str
        @return:
        """
        return str(self.timestamp)

    @property
    def ty_stamp(self):
        """
            TY台风编号_时间戳
            TY2109_2021080415
        @return:
        """
        return f'TY{self.ty_code}_{self.timestamp_str}'

    @property
    def path_result(self) -> str:
        """
            result 的存储目录
            F:\03nginx_data\nmefc_download\TY_GROUP_RESULT\result
        @return:
        """
        result_place: str = 'result'
        return str(pathlib.Path(self.parent_path) / result_place / self.ty_stamp)
        # pass

    @property
    def path_result_full(self) -> str:
        """
            获取 result 保存当前 ty 的  路径
            F:\03nginx_data\nmefc_download\TY_GROUP_RESULT\result\TY2109_2021080415
        @return:
        """
        # return str(pathlib.Path(self.path_result) / self.timestamp_str)
        # TODO:[-] 21-09-08 将读取路径修改为 F:\03nginx_data\nmefc_download\TY_GROUP_RESULT\TY2114_1631082947\result
        return str(pathlib.Path(self.path_result))

    @property
    def path_data_full(self) -> str:
        """
            + 21-09-10 获取 data 的  路径 保存 sites3sz.txt 与 topo3sz.dp
            E:\05DATA\01nginx_data\nmefc_download\TY_GROUP_RESULT\data
        @return:
        """
        stamp_data: str = 'data'
        return str(pathlib.Path(self.parent_path) / stamp_data)

    @property
    def path_pathfiles(self) -> str:
        """
            pathfiles 的存储目录
            F:\03nginx_data\nmefc_download\TY_GROUP_RESULT\pathfiles
        @return:
        """
        pathfiles_place: str = 'pathfiles'
        return str(pathlib.Path(self.parent_path) / pathfiles_place / self.ty_stamp)

    @property
    def path_pathfiles_full(self) -> str:
        """
            获取 pathfiles 保存当前 ty 的  路径
            F:\03nginx_data\nmefc_download\TY_GROUP_RESULT\pathfiles\TY2109_2021080415
        @return:
        """
        return str(pathlib.Path(self.path_pathfiles))

    @abstractmethod
    def to_store(self, **kwargs):
        """
            持久化保存
        @param kwargs:
        @return:
        """
        pass

    @abstractmethod
    def to_do(self, **kwargs):
        """
            + 21-09-01
                执行当前job
        @param kwargs:
        @return:
        """
        pass


class GPUCalculate(IBaseJob):
    def to_do(self, **kwargs):
        pass

    def __init__(self):
        pass

    def to_store(self, **kwargs):
        pass


class JobGetTyDetail(IBaseJob):
    """
        抓取台风信息
    """

    def __init__(self, ty_code: str, timestamp: str = None, list_cmd=[]):
        super(JobGetTyDetail, self).__init__(ty_code, timestamp)
        # 切记 此处 的 list_cmd 是 local 时间
        self.list_cmd = list_cmd

    # def __init__(self, ty_code: str, timestamp: str = None):
    #     """
    #         实例化时就获取当前的时间戳
    #     @param ty_code:
    #     @param timestamp:
    #     """
    #     self.ty_code = ty_code
    #     self.timestamp = timestamp if timestamp else arrow.utcnow().timestamp

    @property
    def list_lons(self):
        """
            由 self.list_cmd 提取的 经度 数组
        @return:
        """
        list_temp = []
        if len(self.list_cmd) > 4:
            list_temp = self.list_cmd[2]
        return list_temp

    @property
    def list_lats(self):
        """
            由 self.list_cmd 提取的 纬度 数组
        @return:
        """
        list_temp = []
        if len(self.list_cmd) > 4:
            list_temp = self.list_cmd[3]
        return list_temp

    @property
    def list_bp(self):
        """
            由 self.list_cmd 提取的 气压 数组
        @return:
        """
        list_temp = []
        if len(self.list_cmd) > 4:
            list_temp = self.list_cmd[4]
        return list_temp

    @property
    def forecast_start_dt_local(self) -> datetime:
        """
            当前获取 台风 路径的 起始预报时间(lcoal time zone)
        @return:
        """
        dt_forecast_str = None
        if len(self.list_cmd) > 4:
            list_dt = self.list_cmd[1]
            if len(list_dt) > 0:
                dt_forecast_str = arrow.get(list_dt[0], 'YYYYMMDDHH', tzinfo='Asia/Shanghai').datetime
        return dt_forecast_str

    @property
    def forecast_start_dt_utc(self) -> datetime:
        """
            + 21-10-22 新加入的 utc 属性
        @return:
        """

        # arrow_utc = arrow.get(self.forecast_start_dt_local).shift(hours=-8)
        arrow_utc = arrow.get(self.forecast_start_dt_local).to('utc')
        return arrow_utc.datetime

    @property
    def forecast_end_dt_local(self) -> datetime:
        dt_forecast = None
        if len(self.list_cmd) > 4:
            list_dt = self.list_cmd[1]
            if len(list_dt) > 0:
                # TODO:[-] 21-10-22 需要手动加入时区为本地时区
                dt_forecast = arrow.get(list_dt[-1], 'YYYYMMDDHH', tzinfo='Asia/Shanghai').datetime
        return dt_forecast

    @property
    def forecast_end_dt_utc(self) -> datetime:
        """
            + 21-10-22 新加入的 utc 属性
        @return:
        """

        arrow_utc = arrow.get(self.forecast_end_dt_local).to('utc')
        return arrow_utc.datetime

    @property
    def list_timeDiff(self):
        list_temp = []
        list_dt_range = []
        if len(self.list_cmd) > 4:
            # ['2021082314', '2021082320']
            list_temp = self.list_cmd[1]
            start_dt_str = list_temp[0]
            start_dt_utc = arrow.get(start_dt_str, 'YYYYMMDDHH').shift(hours=-8)
            second_dt_utc = arrow.get(list_temp[1], 'YYYYMMDDHH').shift(hours=-8)
            # 时间差
            hour_diff: int = int((second_dt_utc.timestamp - start_dt_utc.timestamp) / (60 * 60))
            for temp in range(len(list_temp)):
                list_dt_range.append(temp * hour_diff)

        return list_dt_range

    @except_log()
    def to_do(self, list_customer_cma=None, **kwargs):
        """
            生成台风技术信息 list ，可接受自定义的台风路径
            + 21-09-18
                此处加入了 可选参数 list_customer_cma 传入自定义的 台风路径信息
                # eg: ['TY2112_2021090116_CMA_original',
                        ['2021082314', '2021082320'],
                        ['125.3', '126.6'],
                        ['31.3', '33.8'],
                         ['998', '998'],
                         ['15', '15'],
                         '2112',
                         'OMAIS']
        @param list_customer_cma:
        @param kwargs:
        @return:
        """
        # eg: ['TY2112_2021090116_CMA_original', ['2021082314', '2021082320'], ['125.3', '126.6'], ['31.3', '33.8'], ['998', '998'], ['15', '15'], '2112', 'OMAIS']
        # 是一个嵌套数组
        # list[0] TY2112_2021090116_CMA_original 是具体的编号
        # List[1] ['2021082314', '2021082320'] 时间
        # list[2] ['125.3', '126.6'] 经度
        # list[3] ['31.3', '33.8']   维度
        # list[4] ['998', '998']     气压
        # list[5] ['15', '15']       暂时不用
        if list_customer_cma is None:
            list_customer_cma = []
        list_cmd: List[any] = []

        if len(list_customer_cma) > 0:
            list_cmd = list_customer_cma
        else:
            list_cmd = self.get_typath_cma(SHARED_PATH, self.ty_code)
        self.list_cmd = list_cmd

        # list_lon = list_cmd[2]
        # list_lat = list_cmd[3]
        # list_bp = list_cmd[4]
        pass

    def to_store(self, **kwargs):
        pass

    @store_job_rate(job_instance=JobInstanceEnum.GET_TY_DETAIL, job_rate=10)
    def get_typath_cma(self, wdir0: str, tyno: str, **kwargs):
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
        :param wdir0: 模型根目录
        :param tyno:  台风编号
        :return:['TYtd03_2021071606_CMA_original', ['2021070805', '2021070811', '2021070817'], ['106.3', '104.7', '103.2'], ['19.5', '19.7', '19.9'], ['1000', '1002', '1004'], ['15', '12', '10'], 'TD03', None]
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
                timestamp_str = self.timestamp
                # TODO:[*] 21-09-01 以下替换为 self.timestamp
                # caseno = "TY" + id.lower() + "_" + str(year) + smonth + sday + shrs
                # caseno = "TY" + id.lower() + "_" + timestamp_str
                # wdirp = wdir0 + '/' + 'pathfiles/' + caseno + '/'
                wdirp = self.path_result_full
                if not os.path.exists(wdirp):
                    os.makedirs(wdirp)
                # filename = caseno + "_CMA_original"
                filename = self.ty_stamp + "_CMA_original"
                filename_full_path: str = str(pathlib.Path(wdirp) / filename)
                result = open(filename_full_path, "w+")
                result.write(id + "\n")
                result.write("0" + "\n")
                result.write(str(len(info) - 6) + "\n")
                for j in range(0, len(info) - 6):
                    result.write(str(info[j]) + "\n")
                result.close()
                if id == tyno:
                    outcma = [filename, tcma, loncma, latcma, pcma, spdcma, id, tyname]

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
                    # TODO:[*] 21-09-02 此部分可以提取至外侧 与上面有部分重合
                    # caseno = "TY" + id.lower() + "_" + str(year) + smonth + sday + shrs
                    # wdirp = wdir0 + '/' + 'pathfiles/' + caseno + '/'
                    wdirp = self.path_pathfiles_full
                    if not os.path.exists(wdirp):
                        os.makedirs(wdirp)
                    # filename = caseno + "_CMA_original"
                    filename = self.ty_stamp + "_CMA_original"
                    filename_full_path: str = str(pathlib.Path(wdirp) / filename)
                    result = open(filename_full_path, "w+")
                    result.write(id + "\n")
                    result.write("0" + "\n")
                    result.write(str(len(info) - 7) + "\n")
                    for j in range(0, len(info) - 7):
                        result.write(str(info[j]) + "\n")
                    result.close()
                    if id == tyno:
                        outcma = [filename, tcma, loncma, latcma, pcma, spdcma, id, tyname]
                        kk = kk + 1
                        if kk == 1:
                            break  # 保证找到一条最新的预报结果后退出
        return outcma

    def _spider_ty_info(self, url="http://www.nmc.cn/publish/typhoon/message.html"):
        """
            + 21-09-21 将 原来放在 self.get_typath_cma 中的爬取台风信息的代码封装至此方法中
            返回 爬取后的 台风信息 List
        @return:
        """
        info = None

        import os
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
        return info

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


class JobGetCustomerTyDetail(JobGetTyDetail):

    @except_log()
    def to_do(self, list_customer_cma=None, **kwargs):
        """
            + 21-09-18
                此处加入了 可选参数 list_customer_cma 传入自定义的 台风路径信息
                # eg: ['TY2112_2021090116_CMA_original',
                        ['2021082314', '2021082320'],
                        ['125.3', '126.6'],
                        ['31.3', '33.8'],
                         ['998', '998'],
                         ['15', '15'],
                         '2112',
                         'OMAIS']
        @param list_customer_cma:
        @param kwargs:
        @return:
        """
        # eg: ['TY2112_2021090116_CMA_original', ['2021082314', '2021082320'], ['125.3', '126.6'], ['31.3', '33.8'], ['998', '998'], ['15', '15'], '2112', 'OMAIS']
        # 是一个嵌套数组
        # list[0] TY2112_2021090116_CMA_original 是具体的编号
        # List[1] ['2021082314', '2021082320'] 时间
        # list[2] ['125.3', '126.6'] 经度
        # list[3] ['31.3', '33.8']   维度
        # list[4] ['998', '998']     气压
        # list[5] ['15', '15']       暂时不用
        if list_customer_cma is None:
            list_customer_cma = []
        list_cmd: List[any] = []
        if len(list_customer_cma) > 0:
            list_cmd = self.get_typath_cma(SHARED_PATH, self.ty_code, list_cma=list_customer_cma)
        self.list_cmd = list_cmd

    @store_job_rate(job_instance=JobInstanceEnum.GET_TY_DETAIL, job_rate=10)
    def get_typath_cma(self, wdir0: str, tyno: str, **kwargs):
        """
            重写了集成父类的 获取 typath_cma 数组的方法
            对于传入的 list_cma 修改后返回
        @param wdir0:
        @param tyno:
        @param kwargs: 需要包含 list_cma
        @return: 返回台风信息 数组
        """
        # 原始正常的 数组
        # ['TYtd03_2021071606_CMA_original',                LIST[0] * 需要加上  主要包含预报机构
        #   ['2021070805', '2021070811', '2021070817'],     LIST[1]
        #   ['106.3', '104.7', '103.2'],                    LIST[2]
        #   ['19.5', '19.7', '19.9'],                       LIST[3]
        #   ['1000', '1002', '1004'],                       LIST[4] 气压
        #   ['15', '12', '10'],                             LIST[5] * 风速
        #   'TD03',                                         LIST[6] * 需要加上        主要是台风编号 ，注意是 台风的四位编号
        #   None]                                           LIST[7]

        # - 21-09-21
        # 'customer_ty_cma_list':
        #  list[0] TY2112_2021090116_CMA_original 是具体的编号
        #  List[1] ['2021082314', '2021082320'] 时间
        #  list[2] ['125.3', '126.6'] 经度
        #  list[3] ['31.3', '33.8']   维度
        #  list[4] ['998', '998']     气压
        #  list[5] ['15', '15']       暂时不用
        list_cma_customer: List[any] = kwargs.get('list_cma')
        # 修改 list_cma 的 index=0 -> TY2112_2021090116_CMA_customer
        list_cma_customer[0] = f'TY{self.ty_stamp}_CMA_customer'
        # 追加 tycode 与 None
        list_cma_customer.append(tyno)
        list_cma_customer.append(None)
        return list_cma_customer


class JobGeneratePathFile(IBaseJob):
    """
        生成 ty_pathfile 与 生成批处理文件
    """

    def __init__(self, ty_code: str, timestamp: str = None, list_cmd=[]):
        super(JobGeneratePathFile, self).__init__(ty_code, timestamp)
        self.list_cmd = list_cmd

    def _get_filed_surge_shell_suffix(self, area: ForecastAreaEnum) -> str:
        """
            + 22-01-18:
            获取指定区域的生成逐时场的控制文件shell的后缀
        @param area:
        @return:
        """
        suffix_name: str = 'CTSgpu_sz_plus.exe'
        # 南海，区域3
        if area == ForecastAreaEnum.SCS:
            suffix_name = 'CTSgpu3_plus.exe'
        # 东海，区域2
        elif area == ForecastAreaEnum.ECS:
            suffix_name = 'CTSgpu2_plus.exe'
        # 渤海，区域1
        # TODO:[*] 22-07-15 注意需要替换区域1的plus文件!
        elif area == ForecastAreaEnum.BHI:
            suffix_name = 'CTSgpu1_plus.exe'
        return suffix_name

    def _get_grouppath_surge_shell_suffix(self, area: ForecastAreaEnum) -> str:
        """
            + 22-01-18:
            获取指定区域的生成不同集合路径的控制文件shell的后缀
        @param area:
        @return:
        """
        suffix_name: str = 'CTSgpu_sz.exe'
        # 南海，区域3
        if area == ForecastAreaEnum.SCS:
            suffix_name = 'CTSgpu3.exe'
        # 东海，区域2
        elif area == ForecastAreaEnum.ECS:
            suffix_name = 'CTSgpu2.exe'
        # 渤海，区域1
        elif area == ForecastAreaEnum.BHI:
            suffix_name = 'CTSgpu1.exe'
        return suffix_name

    @property
    def list_lons(self):
        """
            由 self.list_cmd 提取的 经度 数组
        @return:
        """
        list_temp = []
        if len(self.list_cmd) > 4:
            list_temp = self.list_cmd[2]
        return list_temp

    @property
    def list_lats(self):
        """
            由 self.list_cmd 提取的 纬度 数组
        @return:
        """
        list_temp = []
        if len(self.list_cmd) > 4:
            list_temp = self.list_cmd[3]
        return list_temp

    @property
    def list_bp(self):
        """
            由 self.list_cmd 提取的 气压 数组
        @return:
        """
        list_temp = []
        if len(self.list_cmd) > 4:
            list_temp = self.list_cmd[4]
        return list_temp

    @property
    def path_controlfile(self) -> str:
        """
            + 21-09-24
            生成的 shell 控制文件的所在路径
            eg : xxx/control/TYXXXX_xxxxx
        @return:
        """
        contorl_stamp: str = 'control'
        # return str(pathlib.Path(self.parent_path) / contorl_stamp / self.ty_stamp)
        return str(pathlib.Path(self.parent_path) / contorl_stamp)

    @property
    def name_controlfile(self) -> str:
        """
            + 21-09-24
            生成的 shell 控制文件的存储路径
            eg: sz_start_gpu_model_xxxxx.sh
        @return:
        """
        base_file_name: str = 'sz_start_gpu_model'
        base_file_ext: str = '.sh'
        finial_file_name: str = f'{base_file_name}_{self.timestamp_str}{base_file_ext}'
        return finial_file_name

    @property
    def full_path_controlfile(self) -> str:
        """
            + 21-09-24
            生成的 shell 控制文件的全路径
        @return:
        """
        return str(pathlib.Path(self.path_controlfile) / self.name_controlfile)

    @property
    def forecast_start_dt_local(self) -> datetime:
        """
            当前获取 台风 路径的 起始预报时间
        @return:
        """
        dt_forecast_str = None
        if len(self.list_cmd) > 4:
            list_dt = self.list_cmd[1]
            if len(list_dt) > 0:
                dt_forecast_str = arrow.get(list_dt[0], 'YYYYMMDDHH').datetime
        return dt_forecast_str

    @property
    def forecast_start_dt_utc(self) -> datetime:
        """
            + 21-10-22 新加入的 utc 属性
        @return:
        """
        arrow_utc = arrow.get(self.forecast_start_dt_local).to('utc')
        return arrow_utc.datetime

    @property
    def list_timeDiff(self):
        list_temp = []
        list_dt_range = []
        if len(self.list_cmd) > 4:
            # ['2021082314', '2021082320']
            list_temp = self.list_cmd[1]
            start_dt_str = list_temp[0]
            start_dt_utc: arrow = arrow.get(start_dt_str, 'YYYYMMDDHH').shift(hours=-8)
            second_dt_utc: arrow = arrow.get(list_temp[1], 'YYYYMMDDHH').shift(hours=-8)
            # 时间差
            hour_diff: int = int((second_dt_utc.int_timestamp - start_dt_utc.int_timestamp) / (60 * 60))
            for temp in range(len(list_temp)):
                list_dt_range.append(temp * hour_diff)

        return list_dt_range

    @except_log()
    def to_do(self, **kwargs):
        # list_cmd=kwargs.get('list_cmd')
        # 此部分代码之前放在外侧，我移动至main函数内部调用
        now_utc_str = arrow.utcnow().timestamp
        # TODO:[-] 21-09-18 将参数改为动态的
        # dR = 0  # 大风半径增减值
        # r01 = 60
        # r02 = 100
        # r03 = 120
        # r04 = 150
        # r05 = 180
        # pNum = 145
        dR = kwargs.get('max_wind_radius_diff')  # 大风半径增减值
        area = kwargs.get('forecast_area')  # 获取预报区域
        # 'deviation_radius_list':
        #    [{'hours': 96, 'radius': 150},
        #    {'hours': 72, 'radius': 120},
        #    {'hours': 48, 'radius': 100},
        #    {'hours': 24, 'radius': 60}]
        deviation_radius_list: List[any] = kwargs.get('deviation_radius_list')
        list_radius: List[int] = []
        for temp_radius in deviation_radius_list:
            list_radius.append(temp_radius.get('radius'))
        # eg: : [60, 100, 120, 150]
        list_radius = sorted(list_radius)
        # r01 = 60
        # r02 = 100
        # r03 = 120
        # r04 = 150
        # r05 = 180
        pNum = kwargs.get('members_num')
        #     raise ValueError("A value in x_new is above the interpolation "
        # ValueError: A value in x_new is above the interpolation range.
        hrs1, tlon1, tlat1, pres1 = self.interp6h(self.list_timeDiff, self.list_lons, self.list_lats, self.list_bp)
        # ['TYTD03_2020042710_c0_p00', 'TYTD03_2020042710_c0_p05', 'TYTD03_2020042710_c0_p10',...]
        # TODO:[*] 21-10-22 注意此处的时间由 local -> utc
        filename_list = self.gen_typathfile(SHARED_PATH, self.forecast_start_dt_utc, dR, self.ty_stamp, list_radius,
                                            pNum,
                                            tlon1,
                                            tlat1, pres1)
        self.output_controlfile(SHARED_PATH, filename_list, area)
        pass

    def to_store(self, **kwargs):
        pass

    def interp6h(self, horg, lonorg, latorg, porg):
        """
            将输入的 list<string> => ndarray
        :param horg:
        :param lonorg:
        :param latorg:
        :param porg:
        :return:
        """
        h1org = np.arange(0, horg[-1] + 6, 6)
        if len(horg) >= 4:
            # TODO:[*] ValueError: x and y arrays must be equal in length along interpolation axis.
            # TODO:[-] 22-04-12 样条差值 kind="cubic"
            fx = interpolate.interp1d(horg, lonorg)  # "quadratic","cubic"
            fy = interpolate.interp1d(horg, latorg)
            fp = interpolate.interp1d(horg, porg)
        else:
            fx = interpolate.interp1d(horg, lonorg)  # "quadratic","cubic"
            fy = interpolate.interp1d(horg, latorg)
            fp = interpolate.interp1d(horg, porg)
        #     raise ValueError("A value in x_new is above the interpolation "
        # ValueError: A value in x_new is above the interpolation range.
        lon1org = fx(h1org)
        lat1org = fy(h1org)
        p1org = np.round(fp(h1org))
        return h1org, lon1org, lat1org, p1org

    #
    def cal_time_radius_pres(self, p1org, storg, dR):
        dorg = []
        dorg2 = []
        rorg = []
        korg = len(p1org)
        for i in range(korg):
            if p1org[i] > 1000:
                p1org[i] = 1000
            #
            rorg0 = round((1119 * (1010 - p1org[i]) ** -0.805))
            if rorg0 > 80:
                rorg0 = 80
            elif rorg0 <= 20:
                rorg0 = 20
            rorg.append(round(rorg0 + dR))
            st2 = storg + timedelta(days=i * 6 / 24)
            dorg.append(st2.strftime('%m%d%H'))
            dorg2.append(st2.strftime('%m/%d/%H'))
            #
            if rorg[i] > 80:
                rorg[i] = 80
            elif rorg[i] <= 20:
                rorg[i] = 20
        return (dorg, dorg2, p1org, rorg, korg)

    #

    # print(rads)

    # Make typhoon path files
    #
    def output_pathfiles(self, wdir, filename, caseno, ri, dir, datex, tlonx, tlatx, presx, radsx, label):
        kxi = len(tlonx)
        # TODO:[*] 21-09-03 此处建议修改，以下方式可读性太差
        fn = caseno + '_' + dir + str(ri) + '_p' + label
        tyno = caseno[2:6]
        filename.append(fn)
        finial_file_name: str = str(pathlib.Path(wdir) / fn)
        fi = open(finial_file_name, 'w+')
        fi.write(tyno + '\n')
        fi.write('0\n')
        fi.write(str(kxi) + '\n')
        for i in range(kxi):
            # TODO:[-] ! 22-02-09 注意此处保留小数点后四位!
            fi.write(
                datex[i] + ' ' + "{:.4f}".format(tlonx[i]) + ' ' + "{:.4f}".format(tlatx[i]) + ' ' + "{:.0f}".format(
                    presx[i]) + ' ' + "{:.0f}".format(radsx[i]) + '\n')
        fi.close()
        return filename

    # west=102,east=140,south=8,north=32 r01=60; r02=100; r03=120; r04=150; r05=180
    @store_job_rate(job_instance=JobInstanceEnum.GEN_PATH_FILES, job_rate=20)
    def gen_typathfile(self, wdir0, st, dR, caseno, list_radius, pnum, tlon1, tlat1, pres1):
        '''
            生成 file name 集合
            - 21-09-18 将 r01 - r05 的参数去掉，替换为可变长度的 list_radius
        :param wdir0: 存储根目录
        :param st:     预报的起始时间 datetime.datetime
        :param dR:     大风半径的增减值
        :param caseno: case 编号？
        :param r01:    那五个什么半径？单位是什么？
        :param r02:
        :param r03:
        :param r04:
        :param r05:
        :param pnum:   预报成员个数
        :param tlon1:  起始经度——差值到6小时 数组
        :param tlat1:  起始维度——差值到6小时 数组
        :param pres1:  气压——差值到6小时 数组
        :return:
        '''
        pres05 = pres1 + 5
        pres10 = pres1 + 10
        pres_05 = pres1 - 5
        pres_10 = pres1 - 10
        datef, datef2, pres1, rads, kxi = self.cal_time_radius_pres(pres1, st, dR)
        datef, datef2, pres05, rads05, kxi = self.cal_time_radius_pres(pres05, st, dR)
        datef, datef2, pres10, rads10, kxi = self.cal_time_radius_pres(pres10, st, dR)
        datef, datef2, pres_05, rads_05, kxi = self.cal_time_radius_pres(pres_05, st, dR)
        datef, datef2, pres_10, rads_10, kxi = self.cal_time_radius_pres(pres_10, st, dR)

        nrr = round((pnum / 5 - 5) / 4 + 1)
        minsp = 12
        coef = 0.7

        list_radius: List[int] = [0] + list_radius
        # TODO:[-] 21-09-18 此处将半径修改为动态数组
        # rrs = np.array([0, r01, r02, r03, r04, r05])
        rrs = np.array(list_radius)
        x = np.arange(0, 120 + 24, 24)
        x2 = np.arange(0, 120 + 6, 6)
        rrmat = np.zeros((nrr, len(x) - 1))
        rrmat6 = np.zeros((nrr, len(x2) - 1))
        # TODO:[*] 21-09-21 customer 提交 ty_info 后出现错误，以上的 [0,r01 -> r05] 一共应该为6个数
        # ERROR: ValueError: x and y arrays must be equal in length along interpolation axis.
        fr = interpolate.interp1d(x, rrs, kind="slinear")
        rrs6 = np.round(fr(x2))
        rrmat[0, :] = rrs[1:]
        rrmat6[0, :] = rrs6[1:]
        # rrmat6=np.round(rrmat6)

        filename = []
        kk = 0
        #
        # wdir = wdir0 + '/' + 'pathfiles/' + caseno + '/'
        wdir = self.path_pathfiles_full
        # '/my_shared_data/pathfiles/TYTD03_2020042710/'
        # TODO:[-] 21-07-18 此处修改为使用 pathlib 模块进行对路径的操作
        # 注意可能会出现创建多及目录！
        if not pathlib.Path(wdir).is_dir():
            pathlib.Path(wdir).mkdir(parents=True)
        # if not os.path.exists(wdir):
        #     os.mkdir(wdir)
        # wdirx = wdir0 + '/' + 'result/' + caseno + '/'
        wdirx = self.path_result_full
        if not pathlib.Path(wdirx).is_dir():
            pathlib.Path(wdirx).mkdir(parents=True)
        # if not os.path.exists(wdirx):
        #     os.makedirs(wdirx)

        for r in range(nrr - 1):
            r = r + 1
            rrmat[r, :] = np.round(rrmat[0, :] * r / nrr)
            rrmat6[r, :] = np.round(rrmat6[0, :] * r / nrr)
        # print(rrmat6)
        for r in range(nrr):
            # print(r)
            spd0 = []
            dista = []
            angle = []
            tlonl = tlon1.copy()
            tlatl = tlat1.copy()
            tlonr = tlon1.copy()
            tlatr = tlat1.copy()
            tlonf = tlon1.copy()
            tlatf = tlat1.copy()
            tlons = tlon1.copy()
            tlats = tlat1.copy()

            for j in range(kxi - 1):
                # dista.append(geodistance(tlon1[j],tlat1[j],tlon1[j+1],tlat1[j+1]))
                geodict = Geodesic.WGS84.Inverse(tlat1[j], tlon1[j], tlat1[j + 1], tlon1[j + 1])
                dista.append(geodict['s12'] / 1000)
                angle.append(geodict['azi1'] + 360)
                # TODO:[*] 21-09-22 ERROR: ValueError: cannot convert float NaN to integer
                spd0.append(round(dista[j] / 6))
                if spd0[j] < minsp:
                    # TODO:[*] 22-07-29 IndexError: index 20 is out of bounds for axis 1 with size 20
                    rrmat6[r, j] = round(rrmat6[r, j] * coef)
                    if j == kxi - 1:
                        rrmat6[r, j + 1] = round(rrmat6[r, j + 1] * coef)
                # left patb
                geoxyl = Geodesic.WGS84.Direct(tlat1[j + 1], tlon1[j + 1], angle[j] - 360 + 270, rrmat6[r, j] * 1000)
                tlonl[j + 1] = geoxyl['lon2']
                tlatl[j + 1] = geoxyl['lat2']
                # right path
                geoxyr = Geodesic.WGS84.Direct(tlat1[j + 1], tlon1[j + 1], angle[j] - 360 + 90, rrmat6[r, j] * 1000)
                tlonr[j + 1] = geoxyr['lon2']
                tlatr[j + 1] = geoxyr['lat2']
                # fast path
                geoxyf = Geodesic.WGS84.Direct(tlat1[j + 1], tlon1[j + 1], angle[j] - 360, rrmat6[r, j] * 1000)
                tlonf[j + 1] = geoxyf['lon2']
                tlatf[j + 1] = geoxyf['lat2']
                # slow path
                geoxys = Geodesic.WGS84.Direct(tlat1[j + 1], tlon1[j + 1], angle[j] - 360 - 180, rrmat6[r, j] * 1000)
                tlons[j + 1] = geoxys['lon2']
                tlats[j + 1] = geoxys['lat2']
                # print([tlonl[j],tlatl[j]])

            if r == 0:
                # -----------------------------center path------------------------------------#
                filename = self.output_pathfiles(wdir, filename, caseno, r, 'c', datef, tlon1, tlat1, pres1, rads, '00')
                filename = self.output_pathfiles(wdir, filename, caseno, r, 'c', datef, tlon1, tlat1, pres05, rads05,
                                                 '05')
                filename = self.output_pathfiles(wdir, filename, caseno, r, 'c', datef, tlon1, tlat1, pres10, rads10,
                                                 '10')
                filename = self.output_pathfiles(wdir, filename, caseno, r, 'c', datef, tlon1, tlat1, pres_05, rads_05,
                                                 '_05')
                filename = self.output_pathfiles(wdir, filename, caseno, r, 'c', datef, tlon1, tlat1, pres_10, rads_10,
                                                 '_10')

            # -----------------------------right path------------------------------------#
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'r', datef, tlonr, tlatr, pres1, rads, '00')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'r', datef, tlonr, tlatr, pres05, rads05, '05')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'r', datef, tlonr, tlatr, pres10, rads10, '10')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'r', datef, tlonr, tlatr, pres_05, rads_05,
                                             '_05')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'r', datef, tlonr, tlatr, pres_10, rads_10,
                                             '_10')

            # -----------------------------left path------------------------------------#
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'l', datef, tlonl, tlatl, pres1, rads, '00')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'l', datef, tlonl, tlatl, pres05, rads05, '05')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'l', datef, tlonl, tlatl, pres10, rads10, '10')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'l', datef, tlonl, tlatl, pres_05, rads_05,
                                             '_05')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'l', datef, tlonl, tlatl, pres_10, rads_10,
                                             '_10')

            # -----------------------------fast path------------------------------------#
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'f', datef, tlonf, tlatf, pres1, rads, '00')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'f', datef, tlonf, tlatf, pres05, rads05, '05')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'f', datef, tlonf, tlatf, pres10, rads10, '10')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'f', datef, tlonf, tlatf, pres_05, rads_05,
                                             '_05')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 'f', datef, tlonf, tlatf, pres_10, rads_10,
                                             '_10')

            # -----------------------------slow path------------------------------------#
            filename = self.output_pathfiles(wdir, filename, caseno, r, 's', datef, tlons, tlats, pres1, rads, '00')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 's', datef, tlons, tlats, pres05, rads05, '05')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 's', datef, tlons, tlats, pres10, rads10, '10')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 's', datef, tlons, tlats, pres_05, rads_05,
                                             '_05')
            filename = self.output_pathfiles(wdir, filename, caseno, r, 's', datef, tlons, tlats, pres_10, rads_10,
                                             '_10')

        return filename

    # -----------------------------output control file------------------------------------#
    # output gpus_path_list.bat
    @store_job_rate(job_instance=JobInstanceEnum.GEN_CONTROL_FILES, job_rate=30)
    def output_controlfile(self, wdir0, filename, forecast_area: ForecastAreaEnum):
        """
            生成批处理文件，并分类存储
            [*] 21-09-01 注意此处生成的批处理的内容将文件路径写死！
            + 21-09-24 修改为动态路径
            + 21-09-02 此处替换为 linux的 批处理内容
            生成批处理文件
                eg:
                    sz_gpus_path_list.bat
                    sz_start_gpu_model.bat
        @param wdir0:
        @param filename:
        @param forecast_area: + 22-01-18 - 预报区域
        @return:
        """
        # + 21-09-24: 需要先判断存储目录是否存在，不存在则创建
        full_path: pathlib.Path = pathlib.Path(self.path_controlfile)
        full_path_str: str = str(full_path)
        if not full_path.exists():
            full_path.mkdir(parents=True)
        # TODO:[-] 21-09-24 修改了最终存储的文件 full_path
        # file_full_path: str = str(pathlib.Path(wdir0) / 'sz_start_gpu_model.sh')
        file_full_path: str = self.full_path_controlfile
        fi = open(file_full_path, 'w+')
        fi.write('#! /bin/bash' + '\n')
        # TODO:[-] 21-09-24 实际线上的szsurge 的根目录
        # fi.write('wdir="/home/limingjie/szsurge"\n')
        fi.write(f'wdir="{wdir0}"\n')
        fi.write('cd $wdir' + '\n')
        fi.write('echo Working directory: $wdir\n')
        fi.write('date1=$(date "+%Y-%m-%d %H:%M:%S")\n')
        fi.write('startmonth=${date1:0:4}\n')
        fi.write('startday=${date1:5:2}\n')
        fi.write('starthour=${date1:11:2}\n')
        fi.write('startmin=${date1:14:2}\n')
        fi.write('sstartsec=${date1:17:2}\n')
        fi.write('echo StartTime $date1\n')
        fi.write('\n')
        # TODO:[-] 22-01-18 由于调用不同区域加入了根据 预报区域 生成对应调用的shell的调用模型(.exe)的后缀
        field_suffix_name: str = self._get_filed_surge_shell_suffix(forecast_area)  # 为计算逐时增水场的shell语句后缀
        fi.write(f'echo ' + filename[0] + f'|./{field_suffix_name}\n')

        group_path_suffix_name: str = self._get_grouppath_surge_shell_suffix(forecast_area)  # 为计算集合预报路径的shell语句后缀
        for i in range(len(filename)):
            fi.write(f'echo ' + filename[i] + f'|./{group_path_suffix_name}\n')
        fi.write('\n')
        fi.write('date2=$(date "+%Y-%m-%d %H:%M:%S")\n')
        fi.write('echo EndTime $date2\n')

        fi.write(
            'echo $(($(date +%s -d "$date2") - $(date +%s -d "$date1"))) | awk \'{t=split("60 s 60 m 24 h 999 d",a);for(n=1;n<t;n+=2){if($1==0)break;s=$1%a[n]a[n+1]s;$1=int($1/a[n])}print "Elapsed time:",s}\' \n')
        fi.write('\n')
        fi.write('exit\n')
        fi.close()
        return full_path_str

        # print('Control files for Function B are done!')


class JobTaskBatch(IBaseJob):
    """
        + 21-09-03
            新加入的用来执行批处理的 job
    """

    def to_store(self, **kwargs):
        pass

    @except_log()
    def to_do(self, **kwargs):
        """

        @param kwargs: 包含: full_path_controlfile - 控制器文件全路径
        @return:
        """
        full_path_controlfile: str = kwargs.get('full_path_controlfile')
        members_num: int = kwargs.get('members_num')
        self.to_do_task_batch(members_num, full_path_controlfile)
        # 将异常捕捉封装至装饰器中
        # try:
        #     self.to_do_task_batch(145, full_path_controlfile)
        # except CalculateTimeOutError as timeout:
        #     log_in.error(timeout.message)
        #     raise CalculateTimeOutError(timeout.message)
        # except Exception as ex:
        #     log_in.error(ex.args)
        #     raise Exception(ex.args)

    def to_do_task_batch(self, pnum: int, path_control_file: str):
        """
            调用执行模式的脚本，并返回状态信息
        @param pnum: 集合成员数量
        @param path_control_file: 调用脚本文件全路径
        @return:
        """
        # path0 = os.listdir(wdir0+'pathfiles/' + caseno + '/')
        # path0 = self.path_pathfiles_full
        path0 = os.listdir(self.path_pathfiles_full)
        log_in.info(f'当前文件存储pathfiles的目录共有文件{len(path0)}个，判断标准为:{pnum}')  #
        if len(path0) >= pnum:
            # os.startfile(wdir0 + "sz_start_gpu_model.bat")
            # TODO:[-] 21-09-24 修改 控制文件为外部传入的
            # win 版本的
            # os.startfile(self.parent_path + "sz_start_gpu_model.bat")
            # os.startfile(path_control_file)
            # linux 原始版本
            # a = subprocess.check_call('./sz_start_gpu_model.sh', shell=True, cwd=wdir0)
            # TODO:[-] 21-10-13 手动加入对 control 文件夹手动赋予权限的操作
            modify_sh_full_path: str = str(pathlib.Path(MODIFY_CHMOD_PATH) / MODIFY_CHMOD_FILENAME)
            try:
                log_in.info(f'执行{modify_sh_full_path}可执行文件，请注意！！')
                b = subprocess.check_call(modify_sh_full_path, shell=True)
            except Exception as ex:
                log_in.warning(f'执行{modify_sh_full_path}时出错:{ex.args}')
                pass
            log_in.info(f'执行{path_control_file}可执行文件，请注意！！')
            a = subprocess.check_call(path_control_file, shell=True)
            log_in.info(f'执行{path_control_file}完毕，请检查结果。')
            filenum = 0
            job_start_dt: arrow = arrow.utcnow()
            # wdir = wdir0 + 'result/' + caseno + '/'
            wdir = self.path_result_full
            if not os.path.exists(wdir):
                os.makedirs(wdir)
            # while filenum < pnum * 2 + 1:
            #     job_current_dt: arrow = arrow.utcnow()
            #     # 弱当前计算的时间超出了最大时间间隔，则抛出异常
            #     if (job_current_dt - job_start_dt).seconds > MAX_TIME_INTERVAL:
            #         raise CalculateTimeOutError(f'执行作业:{path_control_file}时超时，请检查!')
            #         break
            #     path1 = os.listdir(wdir)
            #     files = []
            #     for fn in path1:
            #         if fn[-4:] == '.dat':
            #             files.append(fn)
            #     filenum = len(files)
            #     time.sleep(0.2)
            log_in.info(f'执行控制文件执行结束，跳出to_do_task_batch')
        else:
            return


# def __init__(self):

class JobTxt2Nc(IBaseJob):
    """
        step-3
        将生成的 结果集(.txt) 转成 .nc 格式
    """

    def to_store(self, **kwargs):
        pass

    @except_log()
    def to_do(self, **kwargs):
        """

        @param kwargs: forecast_start_dt_str: 预报的起始时间 (local) eg: YYYYMMDDhh
                       forecast_start_dt
                       forecast_area: 预报区域枚举

        @return:
        """
        forecast_dt: datetime = kwargs.get('forecast_dt')
        forecast_start_dt: datetime = kwargs.get('forecast_start_dt')
        forecast_start_dt_str: str = kwargs.get('forecast_start_dt_str')
        area: ForecastAreaEnum = kwargs.get('forecast_area')
        # timestamp_str: str = '2021080415'
        # ts_dt: datetime = arrow.get(forecast_start_dt_str, 'YYYYMMDDhh').datetime
        self.txt2nc(SHARED_PATH, self.ty_stamp, forecast_start_dt, area)
        pass

    @store_job_rate(job_instance=JobInstanceEnum.TXT_2_NC, job_rate=90)
    def txt2nc(self, wdir0, caseno, stm, area: ForecastAreaEnum):
        # TODO:[-] 21-09-10 新增部分——解决陆地部分未掩码的bug
        top_dir_path: str = self.path_data_full
        # TODO:[*] 22-06-20 注意此处的地形文件加载时写死的!需要修改
        topo_file_name: str = get_area_dp_file(area)
        top_full_name: str = str(pathlib.Path(top_dir_path) / topo_file_name)
        log_in.info(f'/task/jobs.py->JobTxt2Nc->def txt2nc()|读取地形文件:{top_full_name}')
        # top_full_name: str = str(pathlib.Path(top_dir_path) / '.dp')
        with open(top_full_name, 'r+') as fi:
            dz0 = fi.readlines()
            tpnum = []
            for L in dz0:
                dz0s = L.strip('\n').split()
                tpnum.append(list(map(float, dz0s)))

            topo = np.array(tpnum)
            topo[topo >= 0] = 1
            topo[topo < 0] = np.nan
            # print(topo)
        # wdir = wdir0 + '/' + 'result/' + caseno + '/'
        # wdir = pathlib.Path(wdir0) / 'result' / caseno
        wdir = self.path_result_full
        path1 = os.listdir(wdir)
        fl_name = None
        fl_name2 = None
        tt1 = time.time()
        for i in range(len(path1)):
            if path1[i][0:5] == 'field' and path1[i][-10:] == 'c0_p00.dat':

                # Read ASCII File
                ''''''
                # TODO:[-] 21-09-08 注意此处需要用pathlib进行拼接！
                # fl_name = wdir + path1[i]
                fl_name: str = str(pathlib.Path(wdir) / path1[i])

                # ascii_fl = loadtxt(fl_name, delimiter=' ',dtype=float)
                with open(fl_name, 'r+') as fi:
                    dz1 = fi.readlines()
                    dznum = []
                    for L in dz1:
                        dz3 = L.strip('\n').split()
                        dznum.append(list(map(float, dz3)))
                    ascii_fl = np.array(dznum)
                # print(ascii_fl)
            #
            if path1[i][0:8] == 'maxSurge' and path1[i][-10:] == 'c0_p00.dat':

                # TODO:[-] 21-09-08 注意此处需要用pathlib进行拼接！
                # fl_name2 = wdir + path1[i]
                fl_name2: str = str(pathlib.Path(wdir) / path1[i])
                # ascii_fl = loadtxt(fl_name, delimiter=' ',dtype=float)
                with open(fl_name2, 'r+') as fi:
                    dz1 = fi.readlines()
                    dznum2 = []
                    for L in dz1:
                        dz3 = L.strip('\n').split()
                        dznum2.append(list(map(float, dz3)))
                    max_surge = np.array(dznum2)
                    # TODO:[-] 21-09-10 新增部分——解决陆地部分未掩码的bug
                    # TODO:[*] 22-06-20 此处存在一个bug
                    # ValueError: operands could not be broadcast together with shapes (720,1140) (660,1080)
                    max_surge = max_surge * topo
        # + 22-06-21 动态获取不同预报区域的范围
        forecast_area_range = get_forecast_area_range(area)
        # yy = np.arange(15 + 1 / 120, 26 + 1 / 120, 1 / 60)
        # xx = np.arange(105 + 1 / 120, 123 + 1 / 120, 1 / 60)
        yy = np.arange(forecast_area_range.lat_min + forecast_area_range.step / 2,
                       forecast_area_range.lat_max + forecast_area_range.step / 2, forecast_area_range.step)
        xx = np.arange(forecast_area_range.lon_min + forecast_area_range.step / 2,
                       forecast_area_range.lon_max + forecast_area_range.step / 2, forecast_area_range.step)
        if fl_name != None:
            print(type(ascii_fl), np.shape(ascii_fl))
            tt, mm = np.shape(ascii_fl)
            # print(stm.strftime('%Y-%m-%d-%H'))
            timestr = []
            hours = []
            timenum = []
            dnum = stm.toordinal()
            HH = str(stm.strftime('%H'))
            # + 22-06-21 此处修改为动态获取纬度差/step
            lat_nums = (forecast_area_range.lat_max - forecast_area_range.lat_min) / forecast_area_range.step
            for i in range(int(tt / lat_nums)):
                st2 = stm + timedelta(hours=i + 1)
                timenum.append(dnum + (float(HH) + i + 1) / 24)
                # print(type(dnum),dnum,timenum)
                timestr.append(str(st2))
                hours.append(i + 1)
            # TODO:[*] 22-06-20 ERROR:
            # ValueError: cannot reshape array of size 9849600 into shape (13,660,1080)
            ascii_fl2 = np.reshape(ascii_fl, (len(timestr), len(yy), len(xx)))
            # TODO:[-] 21-09-10 新增部分——解决陆地部分未掩码的bug
            for i in range(len(timestr)):
                ascii_fl2[i] = ascii_fl2[i] * topo

            # Initialize nc file
            out_nc = fl_name[:-4] + '.nc'
            print('output ' + out_nc)
            nc_data = Dataset(out_nc, 'w', format='NETCDF4')
            nc_data.description = 'Storm Surge Field'
            # print('Storm Surge Field, starting time： '+str(stm.strftime('%Y-%m-%d-%H')))

            # dimensions
            lat = nc_data.createDimension('lat', len(yy))
            lon = nc_data.createDimension('lon', len(xx))
            times = nc_data.createDimension('times', len(timestr))  # round(tt/660)

            # Populate and output nc file
            # variables
            lat = nc_data.createVariable('latitude', 'f4', ('lat',))
            lon = nc_data.createVariable('longitude', 'f4', ('lon',))
            times = nc_data.createVariable('times', 'f4', ('times',))
            surge = nc_data.createVariable('surge', 'f4', ('times', 'lat', 'lon',), fill_value=-9999.0)
            # print(shape(lon),shape(lat))
            # print(shape(xx), shape(yy))

            surge.units = 'm'
            lat.units = 'N'
            lon.units = 'E'
            times.units = 'days since 0001-1-0'

            # set the variables we know first
            lat[:] = yy
            lon[:] = xx
            times[:] = timenum
            surge[::] = ascii_fl2  ### THIS LINE IS NOT WORKING!!!!!!!
            nc_data.close()
            print('Time used: {} sec'.format(time.time() - tt1))
        else:
            print('Storm Surge Field files can NOT be found!')
            print('Time used: {} sec'.format(time.time() - tt1))

        if fl_name2 != None:
            print(np.shape(max_surge))
            out_nc2 = fl_name2[:-4] + '.nc'
            print('output ' + out_nc2)
            nc_data2 = Dataset(out_nc2, 'w', format='NETCDF4')
            nc_data2.description = 'Maximum Storm Surge'
            # print('Storm Surge Field, starting time： '+str(stm.strftime('%Y-%m-%d-%H')))

            # dimensions
            lat = nc_data2.createDimension('lat', len(yy))
            lon = nc_data2.createDimension('lon', len(xx))

            # Populate and output nc file
            # variables
            lat = nc_data2.createVariable('latitude', 'f4', ('lat',))
            lon = nc_data2.createVariable('longitude', 'f4', ('lon',))

            maxsurge = nc_data2.createVariable('max_surge', 'f4', ('lat', 'lon',), fill_value=999.0)
            # print(shape(lon), shape(lat))
            # print(shape(xx), shape(yy))

            maxsurge.units = 'm'
            lat.units = 'N'
            lon.units = 'E'

            # set the variables we know first
            lat[:] = yy
            lon[:] = xx
            maxsurge[::] = max_surge
            nc_data2.close()
            print('Time used: {} sec'.format(time.time() - tt1))
        else:
            print('The maximum Storm Surge files can NOT be found!')
            print('Time used: {} sec'.format(time.time() - tt1))


class JobTxt2NcPro(IBaseJob):
    # 增水大于的范围
    _levs: List[float] = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    # 对应的文件名称
    _levs2: List[float] = ['_gt0_5m', '_gt1_0m', '_gt1_5m', '_gt2_0m', '_gt2_5m', '_gt3_0m']

    def __init__(self, ty_code: str, timestamp: str = None):
        super(JobTxt2NcPro, self).__init__(ty_code, timestamp)
        # self._hcma=[0, 12, 24, 36, 48, 60, 72]
        # self._levs: List[float] = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        # self._levs2: List[float] = ['_gt0_5m', '_gt1_0m', '_gt1_5m', '_gt2_0m', '_gt2_5m', '_gt3_0m']
        pass

    def to_store(self, **kwargs):
        pass

    @except_log()
    def to_do(self, **kwargs):
        """

        :param kwargs:  forecast_start_dt
                        forecast_area 预报区域 (22-06-20 新增)
        :return:
        """
        forecast_start_dt: datetime = kwargs.get('forecast_start_dt')
        forecast_area: ForecastAreaEnum = kwargs.get('forecast_area')
        # timestamp_str: str = '2021080415'
        # ts_dt: datetime = arrow.get(timestamp_str, 'YYYYMMDDhh').datetime
        dznum = self.get_maxsurgedata(SHARED_PATH, self.ty_stamp, forecast_start_dt)
        self.gen_prosurge_nc(SHARED_PATH, self.ty_stamp, forecast_start_dt, dznum, self._levs, self._levs2,
                             forecast_area)
        pass

    def get_maxsurgedata(self, wdir0, caseno, st):
        syear = str(st)[0:4]
        # wdir = wdir0 + '/' + 'result/' + caseno + '/'
        # wdir: str = str(pathlib.Path(wdir0) / 'result' / caseno)
        wdir: str = self.path_result_full
        path1 = os.listdir(wdir)
        # nsta=len(site3)
        dflag = 0
        dznum = []
        tt1 = time.time()
        for i in range(len(path1)):
            if path1[i][0:8] == 'maxSurge' and path1[i][-4:] == '.dat':
                print(path1[i])
                dflag = 1
                full_path: str = str(pathlib.Path(wdir) / path1[i])
                with open(full_path, 'r+') as fi:
                    dz0 = fi.readlines()
                    for L in dz0:
                        dz1 = L.strip('\n').split()
                        dz2 = list(map(float, dz1))
                        # dz3=np.flipud(dz2)
                        dznum.append(dz2)
        dznum = np.array(dznum)
        print('Time used: {} sec'.format(time.time() - tt1))
        if dflag == 1:
            print(type(dznum), np.shape(dznum))
            return dznum
        else:
            dznum = []
            return dznum

    @store_job_rate(job_instance=JobInstanceEnum.TXT_2_NC_PRO, job_rate=90)
    def gen_prosurge_nc(self, wdir0, caseno, st, dznum, levs, levs2, area: ForecastAreaEnum):

        # tdir = wdir0 + 'data/'
        # + 22-06-21 动态获取不同预报区域的范围
        forecast_area_range = get_forecast_area_range(area)
        lat_nums = int((forecast_area_range.lat_max - forecast_area_range.lat_min) / forecast_area_range.step)
        tdir = str(pathlib.Path(wdir0) / 'data')
        # TODO:[*] 22-06-20 新加入了动态获取地形文件
        topo_file_name: str = get_area_dp_file(area)
        toponame = str(pathlib.Path(tdir) / topo_file_name)
        with open(toponame, 'r+') as fi:
            dz0 = fi.readlines()
            tpnum = []
            for L in dz0:
                dz0s = L.strip('\n').split()
                tpnum.append(list(map(float, dz0s)))

            topo = np.array(tpnum)
            topo[topo >= 0] = 1
            topo[topo < 0] = np.nan
            # print(topo)
        #
        if dznum == []:
            print('Can NOT find maxsurge files!')
            return
        else:
            tt, mm = np.shape(dznum)
            sur = dznum[0:lat_nums, :]
            sur = np.array(sur)
            sur = np.flipud(sur)
            dznum[dznum > 900] = 0
            # TODO:[-] 22-07-14 改为动态获取 lats 与 lngs
            res_latlngs = get_forecast_area_latlngs(area)
            lon0 = res_latlngs[1]
            lat0 = res_latlngs[0]

            lons, lats = np.meshgrid(lon0, lat0)
            #
            # wdir = wdir0 + 'result/' + caseno + '/'
            # wdir = str(pathlib.Path(wdir0) / 'result' / caseno)
            wdir: str = self.path_result_full
            syear = str(st)[0:4]
            #
            for i in range(len(levs)):
                pps = self.cal_pro(dznum, levs[i], area)
                pps = np.flipud(pps)
                pps[sur > 900] = nan
                ##==============saveas netcdf===================#
                out_filename = 'proSurge_' + caseno + levs2[i] + '.nc'
                out_nc_full_name: str = str(pathlib.Path(wdir) / out_filename)
                # out_nc = wdir + 'proSurge_' + caseno + levs2[i] + '.nc'
                print('output ' + out_nc_full_name)
                if os.path.exists(out_nc_full_name):
                    os.remove(out_nc_full_name)
                nc_data = Dataset(out_nc_full_name, 'w', format='NETCDF4')
                nc_data.description = 'The probability of storm surge >=' + str(levs[i]) + 'm'
                # print('Storm Surge Field, starting time： '+str(stm.strftime('%Y-%m-%d-%H')))

                # dimensions
                lat = nc_data.createDimension('lat', len(lat0))
                lon = nc_data.createDimension('lon', len(lon0))

                # Populate and output nc file
                # variables
                lat = nc_data.createVariable('latitude', 'f4', ('lat',))
                lon = nc_data.createVariable('longitude', 'f4', ('lon',))

                prosurge = nc_data.createVariable('pro_surge', 'f4', ('lat', 'lon',), fill_value=999.0)

                prosurge.units = '%'
                lat.units = 'N'
                lon.units = 'E'
                # set the variables we know first
                lat[:] = lat0
                lon[:] = lon0
                prosurge[::] = pps
                nc_data.close()

    def cal_pro(self, dznum, levs, area: ForecastAreaEnum):
        # + 22-06-21 动态获取不同预报区域的范围
        forecast_area_range = get_forecast_area_range(area)
        lat_nums = int((forecast_area_range.lat_max - forecast_area_range.lat_min) / forecast_area_range.step)
        pp = dznum.copy()
        pp[pp >= levs] = levs
        pp[pp < levs] = 0
        tt, mm = np.shape(dznum)
        pps = np.zeros((lat_nums, mm))
        for i in range(int(tt / lat_nums)):
            pps = pps + pp[i * lat_nums:(i + 1) * lat_nums, :] / levs
        pps = pps / int(tt / lat_nums) * 100
        return pps

        # return picname
