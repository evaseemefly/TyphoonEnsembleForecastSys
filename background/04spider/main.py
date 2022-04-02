# 这是一个示例 Python 脚本。
import requests
import json
from urllib import request


# 按 ⌃F5 执行或将其替换为您的代码。
# 按 双击 ⇧ 在所有地方搜索类、文件、工具窗口、操作和设置。

def custom_post():
    """
        测试抓取台风网的数据
    :return:
    """
    # 指定url
    url = 'http://typhoon.nmc.cn/weatherservice/typhoon/jsons/list_default'
    # 爬取对应指定台风的路径信息
    # http://typhoon.nmc.cn/weatherservice/typhoon/jsons/view_2713966?t=1648868959216&callback=typhoon_jsons_view_2707635
    baseUrl = 'typhoon.nmc.cn'
    # ua伪装
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
    }
    # 自己手动输入区域
    word = input('请输入一个单词')
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
    import http.client
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
    list_typhoons = obj['typhoonList']
    for ty_temp in list_typhoons:
        # [2723975, 'nameless', '热带低压', None, '20210022', 20210022, None, 'stop']
        pass
    pass


def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 F9 切换断点。
    custom_post()


def main():
    custom_post()


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()
    # print_hi('PyCharm')

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
