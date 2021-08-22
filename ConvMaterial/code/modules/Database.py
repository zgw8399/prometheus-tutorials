#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql

from modules.Config import config

"""
    MySQL数据库操作类
"""


class MySQL:
    def __init__(self):
        self.config = config
        self.connection = pymysql.connect(host=self.config['mysql']['host'],
                                          user=self.config['mysql']['user'],
                                          password=self.config['mysql']['password'],
                                          database=self.config['mysql']['database'],
                                          cursorclass=pymysql.cursors.DictCursor)

    def fetch_all(self, kwargs):
        # 获取所有记录
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(kwargs)
                result = cursor.fetchall()
                return result

    def fetch_one(self, kwargs):
        # 获取单条记录
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(kwargs)
                result = cursor.fetchone()
                return result

    def dml(self, kwargs):
        # 数据库DML操作
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(kwargs)
            self.connection.commit()
