#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


def get_all_db():
    """获取所有数据库名称，过滤空字符串并以列表返回"""
    process = os.popen("mysql -BN -e 'show databases'")
    output = process.read().split('\n')
    process.close()

    def not_empty(s):
        return s and s.strip()
    c = filter(not_empty, output)
    return list(c)


print(get_all_db())
