#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tornado.web import RequestHandler
import subprocess
import sys

sys.path.append('../')
import config


# 保留功能
class IndexHandler(RequestHandler):
    def get(self):
        self.write('OK')


# 健康检查功能
class HealthCheckHandler(RequestHandler):
    def get(self):
        self.write('Service is healthy')


# 基类
class BaseHandler(RequestHandler):
    # 设置默认请求头
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Headers', 'Origin, x-Requested-With, Content-Type')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE, OPTIONS')

    # 支持跨域
    def options(self):
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Headers', 'Origin, x-Requested-With, Content-Type')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE, OPTIONS')


# 运行Shell命令的类
class RunCMD(object):
    def __init__(self, command, timeout=5):
        self.command = command
        self.timeout = timeout

    def run(self):
        result = subprocess.run(self.command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",timeout=self.timeout)
        return result


if __name__ == "__main__":
    pass

