from abc import ABCMeta, abstractclassmethod, abstractmethod, ABC
import datetime
import time
import requests
from lxml import etree
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

from model.models import CaseStatus
from conf.settings import TEST_ENV_SETTINGS

SHARED_PATH = TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR')


class IBaseJob(metaclass=ABCMeta):
    def __init__(self, ty_code: str, timestamp: str = None):
        """
            实例化时就获取当前的时间戳
        @param ty_code:
        @param timestamp:
        """
        self.ty_code: str = ty_code
        self.timestamp: int = timestamp if timestamp else arrow.utcnow().timestamp
        self.list_cmd = []

    """
        基础 job 抽象类

    """

    @property
    def ty_stamp(self):
        return f'TY{self.ty_code}_{self.timestamp}'

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
    def __init__(self, ty_code: str, timestamp: str = None, list_cmd=[]):
        super(JobGetTyDetail, self).__init__(ty_code, timestamp)
        self.list_cmd = list_cmd

    # def __init__(self, ty_code: str, timestamp: str = None):
    #     """
    #         实例化时就获取当前的时间戳
    #     @param ty_code:
    #     @param timestamp:
    #     """
    #     self.ty_code = ty_code
    #     self.timestamp = timestamp if timestamp else arrow.utcnow().timestamp

    def to_do(self, **kwargs):
        # eg: ['TY2112_2021090116_CMA_original', ['2021082314', '2021082320'], ['125.3', '126.6'], ['31.3', '33.8'], ['998', '998'], ['15', '15'], '2112', 'OMAIS']
        # 是一个嵌套数组
        # list[0] TY2112_2021090116_CMA_original 是具体的编号
        # List[1] ['2021082314', '2021082320'] 时间
        # list[2] ['125.3', '126.6'] 经度
        # list[3] ['31.3', '33.8']   维度
        # list[4] ['998', '998']     气压
        # list[5] ['15', '15']       暂时不用
        list_cmd = self.get_typath_cma(SHARED_PATH, self.ty_code)
        self.list_cmd = list_cmd
        list_lon = list_cmd[2]
        list_lat = list_cmd[3]
        list_bp = list_cmd[4]
        pass

    def to_store(self, **kwargs):
        pass

    def get_typath_cma(self, wdir0: str, tyno: str):
        """
            TODO:[-] 此处返回值有可能是None，对于不存在的台风编号，则返回空？
                    抓取台风
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
                caseno = "TY" + id.lower() + "_" + timestamp_str
                wdirp = wdir0 + '/' + 'pathfiles/' + caseno + '/'
                if not os.path.exists(wdirp):
                    os.makedirs(wdirp)
                filename = caseno + "_CMA_original"

                result = open(wdirp + filename, "w+")
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
                    caseno = "TY" + id.lower() + "_" + str(year) + smonth + sday + shrs
                    wdirp = wdir0 + '/' + 'pathfiles/' + caseno + '/'
                    if not os.path.exists(wdirp):
                        os.makedirs(wdirp)
                    filename = caseno + "_CMA_original"
                    result = open(wdirp + filename, "w+")
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


class JobGeneratePathFile(IBaseJob):
    def __init__(self, ty_code: str, timestamp: str = None, list_cmd=[]):
        super(JobGeneratePathFile, self).__init__(ty_code, timestamp)
        self.list_cmd = list_cmd

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
    def forecast_start_dt(self) -> datetime:
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

    def to_do(self, **kwargs):
        # list_cmd=kwargs.get('list_cmd')
        # 此部分代码之前放在外侧，我移动至main函数内部调用
        now_utc_str = arrow.utcnow().timestamp
        dR = 0  # 大风半径增减值
        r01 = 60
        r02 = 100
        r03 = 120
        r04 = 150
        r05 = 180
        pNum = 145
        hrs1, tlon1, tlat1, pres1 = self.interp6h(self.list_timeDiff, self.list_lons, self.list_lats, self.list_bp)
        # ['TYTD03_2020042710_c0_p00', 'TYTD03_2020042710_c0_p05', 'TYTD03_2020042710_c0_p10',...]
        filename_list = self.gen_typathfile(SHARED_PATH, self.forecast_start_dt, dR, self.ty_stamp, r01, r02, r03, r04,
                                            r05, pNum,
                                            tlon1,
                                            tlat1, pres1)
        self.output_controlfile(SHARED_PATH, filename_list)
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
            fx = interpolate.interp1d(horg, lonorg, kind="cubic")  # "quadratic","cubic"
            fy = interpolate.interp1d(horg, latorg, kind="cubic")
            fp = interpolate.interp1d(horg, porg, kind="cubic")
        else:
            fx = interpolate.interp1d(horg, lonorg)  # "quadratic","cubic"
            fy = interpolate.interp1d(horg, latorg)
            fp = interpolate.interp1d(horg, porg)
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
        fn = caseno + '_' + dir + str(ri) + '_p' + label
        tyno = caseno[2:6]
        filename.append(fn)
        fi = open(wdir + fn, 'w+')
        fi.write(tyno + '\n')
        fi.write('0\n')
        fi.write(str(kxi) + '\n')
        for i in range(kxi):
            fi.write(
                datex[i] + ' ' + "{:.1f}".format(tlonx[i]) + ' ' + "{:.1f}".format(tlatx[i]) + ' ' + "{:.0f}".format(
                    presx[i]) + ' ' + "{:.0f}".format(radsx[i]) + '\n')
        fi.close()
        return filename

    # west=102,east=140,south=8,north=32 r01=60; r02=100; r03=120; r04=150; r05=180
    def gen_typathfile(self, wdir0, st, dR, caseno, r01, r02, r03, r04, r05, pnum, tlon1, tlat1, pres1):
        '''
            生成 file name 集合
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
        minsp = 12;
        coef = 0.7

        rrs = np.array([0, r01, r02, r03, r04, r05])
        x = np.arange(0, 120 + 24, 24)
        x2 = np.arange(0, 120 + 6, 6)
        rrmat = np.zeros((nrr, len(x) - 1))
        rrmat6 = np.zeros((nrr, len(x2) - 1))
        fr = interpolate.interp1d(x, rrs, kind="slinear")
        rrs6 = np.round(fr(x2))
        rrmat[0, :] = rrs[1:]
        rrmat6[0, :] = rrs6[1:]
        # rrmat6=np.round(rrmat6)

        filename = []
        kk = 0
        #
        wdir = wdir0 + '/' + 'pathfiles/' + caseno + '/'
        # '/my_shared_data/pathfiles/TYTD03_2020042710/'
        # TODO:[-] 21-07-18 此处修改为使用 pathlib 模块进行对路径的操作
        # 注意可能会出现创建多及目录！
        if not pathlib.Path(wdir).is_dir():
            pathlib.Path(wdir).mkdir(parents=True)
        # if not os.path.exists(wdir):
        #     os.mkdir(wdir)
        wdirx = wdir0 + '/' + 'result/' + caseno + '/'
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
            tlonl = tlon1.copy();
            tlatl = tlat1.copy()
            tlonr = tlon1.copy();
            tlatr = tlat1.copy()
            tlonf = tlon1.copy();
            tlatf = tlat1.copy()
            tlons = tlon1.copy();
            tlats = tlat1.copy()

            for j in range(kxi - 1):
                # dista.append(geodistance(tlon1[j],tlat1[j],tlon1[j+1],tlat1[j+1]))
                geodict = Geodesic.WGS84.Inverse(tlat1[j], tlon1[j], tlat1[j + 1], tlon1[j + 1])
                dista.append(geodict['s12'] / 1000)
                angle.append(geodict['azi1'] + 360)
                spd0.append(round(dista[j] / 6))
                if spd0[j] < minsp:
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
    def output_controlfile(self, wdir0, filename):
        """
            TODO:[*] 21-09-01 注意此处生成的批处理的内容将文件路径写死！
            + 21-09-02 此处替换为 linux的 批处理内容
            生成批处理文件
                eg:
                    sz_gpus_path_list.bat
                    sz_start_gpu_model.bat
        :param wdir0:
        :param filename:
        :return:
        """
        fi = open(wdir0 + 'sz_start_gpu_model.sh', 'w+')
        fi.write('#! /bin/bash' + '\n')
        fi.write('wdir="/home/limingjie/szsurge"\n')
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
        fi.write('echo ' + filename[0] + '|./CTSgpu_sz_plus.exe\n')
        for i in range(len(filename)):
            fi.write('echo ' + filename[i] + '|./CTSgpu_sz.exe\n')
        fi.write('\n')
        fi.write('date2=$(date "+%Y-%m-%d %H:%M:%S")\n')
        fi.write('echo EndTime $date2\n')

        fi.write(
            'echo $(($(date +%s -d "$date2") - $(date +%s -d "$date1"))) | awk \'{t=split("60 s 60 m 24 h 999 d",a);for(n=1;n<t;n+=2){if($1==0)break;s=$1%a[n]a[n+1]s;$1=int($1/a[n])}print "Elapsed time:",s}\' \n')
        fi.write('\n')
        fi.write('exit\n')
        fi.close()

        # print('Control files for Function B are done!')


class JobTxt2Nc(IBaseJob):
    """
        step-3
        将生成的 结果集(.txt) 转成 .nc 格式
    """

    def to_store(self, **kwargs):
        pass

    def to_do(self, **kwargs):
        forecast_dt: datetime = kwargs.get('forecast_dt')
        timestamp_str: str = '2021080415'
        ts_dt: datetime = arrow.get(timestamp_str, 'YYYYMMDDhh').datetime
        self.txt2nc(SHARED_PATH, self.ty_stamp, ts_dt)
        pass

    def txt2nc(self, wdir0, caseno, stm):
        wdir = wdir0 + '/' + 'result/' + caseno + '/'
        path1 = os.listdir(wdir)
        fl_name = None
        fl_name2 = None
        tt1 = time.time()
        for i in range(len(path1)):
            if path1[i][0:5] == 'field' and path1[i][-10:] == 'c0_p00.dat':

                # Read ASCII File
                ''''''
                fl_name = wdir + path1[i]
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
                fl_name2 = wdir + path1[i]
                # ascii_fl = loadtxt(fl_name, delimiter=' ',dtype=float)
                with open(fl_name2, 'r+') as fi:
                    dz1 = fi.readlines()
                    dznum2 = []
                    for L in dz1:
                        dz3 = L.strip('\n').split()
                        dznum2.append(list(map(float, dz3)))
                    max_surge = np.array(dznum2)
        #
        yy = np.arange(15 + 1 / 120, 26 + 1 / 120, 1 / 60)
        xx = np.arange(105 + 1 / 120, 123 + 1 / 120, 1 / 60)
        if fl_name != None:
            print(type(ascii_fl), np.shape(ascii_fl))
            tt, mm = np.shape(ascii_fl)
            # print(stm.strftime('%Y-%m-%d-%H'))
            timestr = []
            hours = []
            timenum = []
            dnum = stm.toordinal()
            HH = str(stm.strftime('%H'))
            for i in range(int(tt / 660)):
                st2 = stm + timedelta(hours=i + 1)
                timenum.append(dnum + (float(HH) + i + 1) / 24)
                # print(type(dnum),dnum,timenum)
                timestr.append(str(st2))
                hours.append(i + 1)

            ascii_fl2 = np.reshape(ascii_fl, (len(timestr), len(yy), len(xx)))

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
    def to_store(self, **kwargs):
        pass

    def to_do(self, **kwargs):
        pass

    def get_maxsurgedata(self, wdir0, caseno, st):
        syear = str(st)[0:4]
        wdir = wdir0 + 'result/' + caseno + '/'
        path1 = os.listdir(wdir)
        # nsta=len(site3)
        dflag = 0
        dznum = []
        tt1 = time.time()
        for i in range(len(path1)):
            if path1[i][0:8] == 'maxSurge' and path1[i][-4:] == '.dat':
                print(path1[i])
                dflag = 1

                with open(wdir + path1[i], 'r+') as fi:
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

    def gen_prosurge_nc(self, wdir0, caseno, st, dznum, levs, levs2):
        tdir = wdir0 + 'data/'
        toponame = tdir + 'topo3sz.dp'
        # TODO:[*] FileNotFoundError: [Errno 2] No such file or directory: '/my_shared_data/data/topo3sz.dp'
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
            sur = dznum[0:660, :]
            sur = np.array(sur)
            sur = np.flipud(sur)
            dznum[dznum > 900] = 0
            lon0 = np.arange(105 + 1 / 120, 123 + 1 / 120, 1 / 60)
            lat0 = np.arange(15 + 1 / 120, 26 + 1 / 120, 1 / 60)
            lons, lats = np.meshgrid(lon0, lat0)
            #
            wdir = wdir0 + 'result/' + caseno + '/'
            syear = str(st)[0:4]
            #
            for i in range(len(levs)):
                pps = self.cal_pro(dznum, levs[i])
                pps = np.flipud(pps)
                pps[sur > 900] = nan
                ##==============saveas netcdf===================#
                out_nc = wdir + 'proSurge_' + caseno + levs2[i] + '.nc'
                print('output ' + out_nc)
                if os.path.exists(out_nc):
                    os.remove(out_nc)
                nc_data = Dataset(out_nc, 'w', format='NETCDF4')
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

    def cal_pro(self, dznum, levs):
        pp = dznum.copy()
        pp[pp >= levs] = 1
        pp[pp < levs] = 0
        tt, mm = np.shape(dznum)
        pps = np.zeros((660, mm))
        for i in range(int(tt / 660)):
            pps = pps + pp[i * 660:(i + 1) * 660, :]
        pps = pps / int(tt / 660) * 100
        return pps

        # return picname
