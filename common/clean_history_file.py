#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import os
import shutil


def clean_history_file(file_path, keep_num):
    """实现自动保留ctime最近的几个文件"""
    file_list = os.listdir(file_path)
    d = {}
    for file_name in file_list:
        full_name = os.path.join(file_path, file_name)
        ctime = os.path.getctime(full_name)
        d[full_name] = ctime
    ctime_list = sorted(d.items(), key=lambda item: item[1])
    # sorted方法可按照字典的key和value进行排序
    # 这里的key是一个lambda函数，表示按照选取元组d.items()中的第二个元素进行排序
    if len(ctime_list) <= keep_num:
        return '无'
    else:
        del_list = []
        for i in range(len(ctime_list) - keep_num):
            if os.path.isfile(ctime_list[i][0]):
                # '''ctime_list[i][0]'''取ctime_list中的第i个元素，然后取第i个元素中的第0个元素
                os.remove(ctime_list[i][0])
            else:
                shutil.rmtree(ctime_list[i][0])
            del_list.append(ctime_list[i][0])
        return del_list


file_path = '/remote/backups'
del_files = clean_history_file(file_path, 3)
print(del_files)
