#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


def get_cmd_output(cmd):
    """获取Shell命令输出"""
    process = os.popen(cmd)
    output = process.read()
    process.close()
    return output


cmd = "mysql -BN -e 'show master status' | cut -f1"
print(get_cmd_output(cmd).strip().split()[0])
