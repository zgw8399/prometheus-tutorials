#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def size_conversion(size):
    """
    实现文件数据大小单位转换。
    递归实现，精确为最大单位值 + 小数点后三位。
    """
    def conversion(integer, remainder, level):
        if integer >= 1024:
            remainder = integer % 1024
            integer //= 1024
            level += 1
            return conversion(integer, remainder, level)
        else:
            return integer, remainder, level

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    integer, remainder, level = conversion(size, 0, 0)
    if level+1 > len(units):
        level = -1
    return ('{}.{:>03d} {}'.format(integer, remainder, units[level]))


print(size_conversion(100))
print(size_conversion(1024))
print(size_conversion(1024*1024))
print(size_conversion(1024*1024*1024))
print(size_conversion(1024*1024*1024*1024))
print(size_conversion(1024*1024*1024*1024*1024))
