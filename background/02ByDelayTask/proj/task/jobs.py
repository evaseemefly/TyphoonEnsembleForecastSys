from abc import ABCMeta, abstractclassmethod, abstractmethod, ABC
import datetime
import requests
from lxml import etree
import arrow

from model.models import CaseStatus
from conf.settings import TEST_ENV_SETTINGS

SHARED_PATH = TEST_ENV_SETTINGS.get('TY_GROUP_PATH_ROOT_DIR')


class IBaseJob(metaclass=ABCMeta):
    """
        基础 job 抽象类

    """

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
    def __init__(self, ty_code: str, timestamp: str = None):
        """
            实例化时就获取当前的时间戳
        @param ty_code:
        @param timestamp:
        """
        self.ty_code = ty_code
        self.timestamp = timestamp if timestamp else arrow.utcnow().timestamp
        # self.timestamp = arrow.utcnow().timestamp

    def to_do(self, **kwargs):
        out_cma = self.get_typath_cma(SHARED_PATH, self.ty_code)
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
            info = self.parse_first(forecast)
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
                year = datetime.datetime.now().year
                month = datetime.datetime.now().month
                day = datetime.datetime.now().day
                hour = datetime.datetime.now().hour
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
                wdirp = wdir0 + 'pathfiles/' + caseno + '/'
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
                info = self.parse_info(contents, item)
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

                    year = datetime.datetime.now().year
                    month = datetime.datetime.now().month
                    day = datetime.datetime.now().day
                    hour = datetime.datetime.now().hour
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
                    wdirp = wdir0 + 'pathfiles/' + caseno + '/'
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

    def parse_info(self, list, time_issu):
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

                    time1 = datetime.datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S') + datetime.timedelta(hours=8)
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
                    time1 = datetime.datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S') + datetime.timedelta(
                        hours=8) + datetime.timedelta(hours=int(hr))
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

    def parse_first(self, list):
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
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
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

                time1 = datetime.datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S') + datetime.timedelta(hours=8)
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
                time1 = datetime.datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S') + datetime.timedelta(
                    hours=8) + datetime.timedelta(hours=int(hr))
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
