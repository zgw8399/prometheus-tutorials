#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def read_file(file_name):
    """读取文件"""
    with open(file_name, 'r') as f:
        return f.read()


print(read_file('/data/backups/last_backup').strip().split()[0])
