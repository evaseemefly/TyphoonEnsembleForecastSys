# 这是一个示例 Python 脚本。
import requests
import json
from urllib import request
import http.client
import datetime
import arrow


# 按 ⌃F5 执行或将其替换为您的代码。
# 按 双击 ⇧ 在所有地方搜索类、文件、工具窗口、操作和设置。

class TyDetailMidModel:
    def __init__(self, ty_code: str, id: int, ty_name_en: str = None, ty_name_ch: str = None):
        self.ty_code = ty_code
        self.id = id
        self.ty_name_en = ty_name_en
        self.ty_name_ch = ty_name_ch

    def __str__(self) -> str:
        return f'TyDetailMidModel:id:{self.id}|ty_code:{self.ty_code}|name_en:{self.ty_name_en}|name_ch：{self.ty_name_ch}'


class TyPathMidModel:
    def __init__(self, ty_id: int, ty_code: str, ty_name_en: str, ty_name_ch: str, ty_path_list: [] = []):
        """

        :param ty_id:
        :param ty_code:
        :param ty_name_en:
        :param ty_name_ch:
        :param ty_rate:
        :param ty_stamp:
        """
        self.ty_id = ty_id
        self.ty_code = ty_code
        self.ty_name_en = ty_name_en
        self.ty_name_ch = ty_name_ch
        self.ty_path_list = ty_path_list

        # self.ty_stamp = ty_stamp

    # @property
    # def ty_forecast_dt(self) -> datetime.datetime:
    #     return arrow.get(self.ty_stamp).datetime


class TyForecastRealDataMidModel:
    def __init__(self, lat: float, lon: float, bp: float, ts: int, ty_type: str):
        """

        :param lat:
        :param lon:
        :param bp:
        :param ts:
        :param ty_type:
        """
        self.lat = lat
        self.lon = lon
        self.bp = bp
        self.ts = ts
        self.ty_type = ty_type


def spider_check_ty_exist(ty_code: str) -> TyDetailMidModel:
    """
        测试抓取台风网的数据
    :return:
    """
    # 指定url
    url = 'http://typhoon.nmc.cn/weatherservice/typhoon/jsons/list_default'
    # 爬取对应指定台风的路径信息
    # view_xxx 即是台风对应的id
    # http://typhoon.nmc.cn/weatherservice/typhoon/jsons/view_2726099
    baseUrl = 'typhoon.nmc.cn'
    ty_obj: TyDetailMidModel = None
    # 方式1：
    # ua伪装
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
    }

    # 定义参数
    param = {
    }
    # 发出请求
    # response = requests.get(url=url, params=param, headers=headers)  # 通过抓包工具看request method判断是post还是get
    # text = response.text  # 通过抓包工具看content-type看是text还是json
    # ---
    # res = request.urlopen(url)
    # content = res.read()
    # cont = json.loads(content.decode('utf-8'))
    # print(cont)
    # -- 方式2 ---
    # 使用 urllib.request 的方式请求，并不好用
    # with request.urlopen(url) as resource:
    #     data = resource.read()
    #     print(f'status:{resource.statues},{resource.reason}')
    #     res = data.decode('utf-8')
    #     print(f'data:{res}')
    #     cont = json.load(resource)

    # -- 方式3 --
    # 参考文章: https://blog.csdn.net/xietansheng/article/details/115557974

    conn = http.client.HTTPConnection(baseUrl)
    conn.request('GET', "/weatherservice/typhoon/jsons/list_default")
    res = conn.getresponse()
    content = res.read().decode('utf-8')
    '''
        typhoon_jsons_list_default(({ "typhoonList":[[2723.....]
                                    }))
    '''
    '''
        { "typhoonList":[[2723.....]
                                    }
    '''
    new_json = '{' + content[29: -3] + '}'

    print(content)
    obj = json.loads(new_json, strict=False)
    # 找到所有台风的集合
    # if obj.hasattr('typhoonList'):
    # 注意判断字典中是否包含指定key,不能使用 hasattr 的方法进行panduan
    # if hasattr(obj, 'typhoonList'):
    if 'typhoonList' in obj.keys():
        list_typhoons = obj['typhoonList']
        for ty_temp in list_typhoons:
            # [2723975, 'nameless', '热带低压', None, '20210022', 20210022, None, 'stop']
            # 根据台风编号找到是否存在对应的台风，并获取台风 英文名(index=1)+中文名(index=2)+台风路径网的id(index=0)
            temp_code: str = ty_temp[4]
            if temp_code == ty_code:
                temp_id: int = ty_temp[0]
                temp_name_ch: str = ty_temp[2]
                temp_name_en: str = ty_temp[1]
                ty_obj = TyDetailMidModel(ty_code, temp_id, temp_name_en, temp_name_ch)
                break
            pass
        pass

    return ty_obj


def spider_get_ty_path(ty_id: int, ty_code: str, ty_name_en: str = 'nameless') -> TyPathMidModel:
    """
        + 22-04-05 获取对应的台风路径
    :param ty_id:
    :param ty_code:
    :param ty_name_en:
    :return:
    """
    baseUrl: str = 'typhoon.nmc.cn'
    # http://typhoon.nmc.cn/weatherservice/typhoon/jsons/view_2726099
    # target_url = f'{url}_{ty_id}'
    conn = http.client.HTTPConnection(baseUrl)
    conn.request('GET', f"/weatherservice/typhoon/jsons/view_{str(ty_id)}")
    res = conn.getresponse()
    content = res.read().decode('utf-8')
    index: int = len(f'typhoon_jsons_view_{str(ty_id)}') + 1
    new_json = content[index:-1]

    #    raise JSONDecodeError("Extra data", s, end)
    # json.decoder.JSONDecodeError: Extra data: line 1 column 10 (char 9)
    '''
        typhoon_jsons_view_2726099(
            {"typhoon":
                [2726099,
                "NYATOH",
                "妮亚图",
                2121,
                2121,
                null,
                "名字来源：马来西亚；意为：一种在东南亚热带雨林环境中生长的树木。",
                "stop",
                [
                    [
                0   2726232,    
                1    "202111300000",
                2    1638230400000,  //ts
                3    "TS",   // ty_type 
                4    139.2,  // 经度-lon
                5    12.6,   // 纬度-lat
                6    998,   // bp
                7    18,
                8    "WNW",
                9    15,
                10    [...]
                    ],
                    ...
                ]
    '''
    ty_path_obj = json.loads(new_json, strict=False)
    tyPathMidModel: TyPathMidModel = {}
    if 'typhoon' in ty_path_obj.keys():
        ty_group_detail = ty_path_obj['typhoon']

        ty_group_list: [] = ty_group_detail[8]
        ty_realdata_list: [] = []
        for temp_ty_group in ty_group_list:
            ty_realdata_list.append(
                TyForecastRealDataMidModel(temp_ty_group[5], temp_ty_group[4], temp_ty_group[6], temp_ty_group[2],
                                           temp_ty_group[3]))
            pass
        tyPathMidModel = TyPathMidModel(ty_group_detail[0], ty_group_detail[3], ty_group_detail[1], ty_group_detail[2],
                                        ty_realdata_list)
    return tyPathMidModel


def main():
    ty_obj = spider_check_ty_exist('2021')
    print(ty_obj)
    if ty_obj is None:
        pass
    ty_group = spider_get_ty_path(ty_obj.id, ty_obj.ty_code, ty_obj.ty_name_en)

    pass


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()
    # print_hi('PyCharm')

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
