#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from pymongo import MongoClient

now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

#client = MongoClient("mongodb://root:123456@127.0.0.1:27017/admin")
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client['test']

print("start_time:", now_time)

i = 0
for i in range(1000000):
    db.test.insert_one({"name": "Tom", "age": "18"})
    i += 1

print("end_time:", now_time)
