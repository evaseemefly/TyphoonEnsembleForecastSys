# from consulate import Consul
import consul

from random import randint
import requests
import json
from typing import List


# consul 操作类
# 初始化，指定 consul 主机、端口和 token
class ConsulClient:
    def __init__(self, consul_host=None, consul_port=None, token=None):
        self.consul_host = consul_host  # consul 主机
        self.consul_port = consul_port  # consul 端口
        self.token = token
        self.consul_client = consul.Consul(host=consul_host, port=consul_port)

    def register(self, name, service_id, service_address, service_port, tags: List[str] = ['master'],
                 interval: str = '30s',
                 ):  # 注册服务 注册服务的服务名  端口  以及 健康监测端口
        # TODO:[*] 23-06-25 check 不论使用 tcp|http 均会出现 Health Status Failing
        # service:typhoon_forecast_geo_v1_geolocalhost:5000
        # 实际路径为 http://128.5.9.79:8092
        check = consul.Check().http(url=f'http://{service_address}:{service_port}/common/consul/check', interval='10s',
                                    timeout='30s')
        # check=consul.Check.tcp(host=service_address,port=service_port,)
        # Get "http://127.0.0.1:5000/health": dial tcp 127.0.0.1:5000: connect: connection refused
        # check = consul.Check.tcp('127.0.0.1', 8000, '5s', '30s', '30s')
        # TODO[*] 修改后仍出现以下错误: Get "http://127.0.0.1:8000/common/consul/check": dial tcp 127.0.0.1:8000: connect: connection refused
        # service_info = {
        #     'Name': name,
        #     'ID': service_id,
        #     'Address': '127.0.0.1',
        #     'Port': 8000,
        #     'Check': {
        #         'TCP': '127.0.0.1:8000',
        #         'Interval': '5s',
        #         'Timeout': '1s',
        #         'DeregisterCriticalServiceAfter': '10s'
        #     }
        # }
        # 使用 0.0.0.0 consul.base.BadRequest: 400 Invalid service address
        self.consul_client.agent.service.register(name=name, service_id=f'{name}_v1', address=service_address,
                                                  port=service_port,
                                                  tags=tags,
                                                  # 心跳检查：间隔：5s，超时：30s，注销：30s
                                                  check=check,
                                                  interval=interval)
        # self.consul_client.agent.service.register(service_info)

    # 负债均衡获取服务实例
    def getService(self, name):
        # 获取相应服务下的 DataCenter
        url = 'http://' + self.consul_host + ':' + str(self.consul_port) + '/v1/catalog/service/' + name
        dataCenterResp = requests.get(url)
        if dataCenterResp.status_code != 200:
            raise Exception('can not connect to consul ')
        listData = json.loads(dataCenterResp.text)
        # 初始化 DataCenter
        dcset = set()
        for service in listData:
            dcset.add(service.get('Datacenter'))
        # 服务列表初始化
        serviceList = []
        for dc in dcset:
            if self.token:
                url = f'http://{self.consul_host}:{self.consul_port}/v1/health/service/{name}?dc={dc}&token={self.token}'
            else:
                url = f'http://{self.consul_host}:{self.consul_port}/v1/health/service/{name}?dc={dc}&token='
            resp = requests.get(url)
            if resp.status_code != 200:
                raise Exception('can not connect to consul ')
            text = resp.text
            serviceListData = json.loads(text)

            for serv in serviceListData:
                status = serv.get('Checks')[1].get('Status')
                # 选取成功的节点
                if status == 'passing':
                    address = serv.get('Service').get('Address')
                    port = serv.get('Service').get('Port')
                    serviceList.append({'port': port, 'address': address})
        if len(serviceList) == 0:
            raise Exception('no serveice can be used')
        else:
            # 随机获取一个可用的服务实例
            print('当前服务列表：', serviceList)
            service = serviceList[randint(0, len(serviceList) - 1)]
            return service['address'], int(service['port'])
