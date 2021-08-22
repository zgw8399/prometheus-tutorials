#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from handlers.base import IndexHandler, HealthCheckHandler
from handlers.convmaterial import ConvMaterialHandler


# 路由映射
handlers = [
    # 保留路径
    (r"/", IndexHandler),
    # 健康检查
    (r"/healthz", HealthCheckHandler),
    # 例子
    (r"/api/v1/ConvMaterial", ConvMaterialHandler),
]


if __name__ == "__main__":
    pass
