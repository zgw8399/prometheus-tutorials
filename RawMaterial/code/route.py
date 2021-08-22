#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from handlers.base import IndexHandler, HealthCheckHandler
from handlers.rawmaterial import RawMaterialHandler
from handlers.supplier import SupplierHandler
from handlers.recipebind import RecipeBindHandler
from handlers.variablebind import VariableBindHandler
from handlers.vehiclestorage import VehicleStorageHandler


# 路由映射
handlers = [
    # 保留路径
    (r"/", IndexHandler),
    # 健康检查
    (r"/healthz", HealthCheckHandler),
    # 料号维护
    (r"/api/v1/RawMaterial", RawMaterialHandler),
    # 供应商维护
    (r"/api/v1/Supplier", SupplierHandler),
    # 配方绑定
    (r"/api/v1/RecipeBind", RecipeBindHandler),
    # 变量绑定
    (r"/api/v1/VariableBind", VariableBindHandler),
    # 车载入库
    (r"/api/v1/VehicleStorage", VehicleStorageHandler),
]


if __name__ == "__main__":
    pass
