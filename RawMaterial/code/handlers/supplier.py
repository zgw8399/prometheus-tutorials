#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import json

from handlers.base import BaseHandler
from modules.Config import config

"""供应商维护"""


class SupplierHandler(BaseHandler):
    # 数据库连接初始化
    def initialize(self):
        self.client = pymongo.MongoClient(**config['mongo'])
        self.db = self.client[config['db']['mes_db_name']]
        self.coll = self.db[config['coll']['supplier_coll_name']]

    # 查询信息
    def get(self):
        try:
            if self.get_argument('SupplierID', ''):
                query = {
                    "SupplierID": self.get_argument('SupplierID')
                }
                data = {
                    "state": "success",
                    "message": "查询成功！",
                    "payload": self.coll.find_one(query, {"_id": 0})
                }
                self.write(json.dumps(data))
            else:
                data = {
                    "state": "success",
                    "message": "查询成功！",
                    "payload":  [x for x in self.coll.find({}, {"_id": 0})]
                }
                self.write(json.dumps(data))
        except:
            data = {
                "state": "failure",
                "message": "查询失败！",
                "payload": ""
            }
            self.write(json.dumps(data))

    # 添加信息
    def post(self):
        try:
            request_data = json.loads(self.request.body.decode('utf-8'))
            query = {
                "SupplierID": request_data.get('SupplierID')
            }
            if self.coll.find_one(query):
                data = {
                    "state": "failure",
                    "message": "信息已存在，请勿重复添加！",
                    "payload": ""
                }
                self.write(json.dumps(data))
            else:
                self.coll.insert_one(request_data)
                data = {
                    "state": "success",
                    "message": "添加成功！",
                    "payload": ""
                }
                self.write(json.dumps(data))
        except:
            data = {
                "state": "failure",
                "message": "添加失败！",
                "payload": ""
            }
            self.write(json.dumps(data))

    # 修改信息
    def put(self):
        try:
            request_data = json.loads(self.request.body.decode('utf-8'))
            query = {
                "SupplierID": request_data.get('SupplierID')
            }
            values = {
                "$set": request_data
            }
            self.coll.update_one(query, values, upsert=True)
            data = {
                "state": "success",
                "message": "修改成功！",
                "payload": ""
            }
            self.write(json.dumps(data))
        except:
            data = {
                "state": "failure",
                "message": "修改失败！",
                "payload": ""
            }
            self.write(json.dumps(data))

    # 删除信息
    def delete(self):
        try:
            request_data = json.loads(self.request.body.decode('utf-8'))
            query = {
                "SupplierID": request_data.get('SupplierID')
            }
            self.coll_vehiclestorage = self.db[config['coll']['vehiclestorage_coll_name']]
            if self.coll_vehiclestorage.find_one(query):
                data = {
                   "state": "failure",
                   "message": "已有关联数据，不允许删除！",
                   "payload": ""
                }
                self.write(json.dumps(data))
            else:
                self.coll.delete_one(query)
                data = {
                    "state": "success",
                    "message": "删除成功！",
                    "payload": ""
                }
                self.write(json.dumps(data))
        except:
            data = {
                "state": "failure",
                "message": "删除失败！",
                "payload": ""
            }
            self.write(json.dumps(data))

    # 数据库连接关闭
    def on_finish(self):
        self.client.close()


if __name__ == "__main__":
    pass
