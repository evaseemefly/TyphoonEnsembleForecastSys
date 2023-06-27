#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from typing import List

import consul
from util.consulclient import ConsulClient


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TyphoonForecastSite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


class DjangoServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # appname 代表微服务的 API 路由路径
        self.appname: str = 'typhoon_forecast'

    def run(self):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TyphoonForecastSite.settings')
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc
        execute_from_command_line(sys.argv)


class HttpServer:
    # 新建服务时，需要指定 consul 服务的 主机，端口，所启动的 服务的 主机 端口 以及 restful http 服务 类
    def __init__(self, service_host, service_port, consul_host, consul_port, appClass, consul_area_name: str,
                 version: str = 'v1'):
        self.service_port = service_port
        self.service_host = service_host
        self.app = appClass(host=service_host, port=service_port)
        # 注意此处需要与 TyphoonForecastSite.url.py 关联
        self.appnames: List[str] = ['station', 'typhoon', 'geo']
        self.consul_host = consul_host
        self.consul_port = consul_port
        self.consul_area_name: str = consul_area_name
        self.version = version

    def startServer(self):
        """
            注册服务
        @return:
        """
        client = ConsulClient(consul_host=self.consul_host, consul_port=self.consul_port)
        # 注册服务，将路由 index 和 user 依次注册
        for aps in self.appnames:
            service_id = aps + self.service_host + ':' + str(self.service_port)
            httpcheck = f'http://{self.service_host}:{str(self.service_port)}/check'
            register_name: str = f'{self.consul_area_name}_{aps}_{self.version}'
            client.register(name=register_name, service_id=service_id, service_address=self.service_host,
                            service_port=self.service_port,
                            tags=["master", "typhoon"])
        # 启动服务
        self.app.run()


if __name__ == '__main__':
    # TODO:[-] 23-06-25 加入了服务注册功能(使用consul)
    # main()
    # 尝试多个 service host 端口
    # 127.0.0.1 不行
    # 0.0.0.0 错误  consul.base.BadRequest: 400 Invalid service address
    # 线上部署可行
    server = HttpServer(service_host='128.5.9.79', service_port=8092, consul_host='128.5.9.79', consul_port=8500,
                        appClass=DjangoServer, consul_area_name='typhoon_forecast')
    server.startServer()
