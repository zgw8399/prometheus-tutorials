#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import json

from base import BaseHandler, config


class ModelHandler(BaseHandler):
    # 数据库连接初始化
    def initialize(self):
        self.client = pymongo.MongoClient(**config.mongodb_options)
        self.db = self.client[config.db['tlink_db_name']]
        self.coll = self.db[config.coll['model_coll_name']]

    # 查询设备型号信息
    def get(self):
        #try:
           if self.get_argument('EquipmentModelID',''):
               query = {
                   "EquipmentModelID": self.get_argument('EquipmentModelID')
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
        #except:
        #    data = {
        #        "state": "failure",
        #        "message": "查询失败！",
        #        "payload": ""
        #    }
        #    self.write(json.dumps(data))

    # 添加设备型号信息
    def post(self):
        #try:
           request_data = json.loads(self.request.body.decode('utf-8'))
           query = {
               "EquipmentModelID": request_data.get('EquipmentModelID')
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
        #except:
        #   data = {
        #       "state": "failure",
        #       "message": "添加失败！",
        #       "payload": ""
        #   }
        #   self.write(json.dumps(data))

    # 修改设备型号信息
    def put(self):
        #try:
           request_data = json.loads(self.request.body.decode('utf-8'))
           query = {
               "EquipmentModelID": request_data.get('EquipmentModelID')
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
        #except:
        #    data = {
        #        "state": "failure",
        #        "message": "修改失败！",
        #        "payload": ""
        #    }
        #    self.write(json.dumps(data))

    # 删除设备型号信息
    def delete(self):
        #try:
           request_data = json.loads(self.request.body.decode('utf-8'))
           query = {
               "EquipmentModelID": request_data.get('EquipmentModelID')
           }
           self.coll_equipment = self.db[config.coll['equipment_coll_name']]
           if self.coll_equipment.find_one(query):
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
        #except:
        #    data = {
        #        "state": "failure",
        #        "message": "删除失败！",
        #        "payload": ""
        #    }
        #    self.write(json.dumps(data))

    # 数据库连接关闭
    def on_finish(self):
        self.client.close()


if __name__ == "__main__":
    pass

