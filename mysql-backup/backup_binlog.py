#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import os.path
import sys
import time
import datetime
import shutil

"""===备份环境==="""

# 本地备份路径
backup_path = '/data/backups/binlog'
# 远程主机
remote_host = 'varden.host'
# 远程主机备份路径
remote_path = '/remote/backups/binlog'
# 二进制日志文件路径
binlog_path = '/var/lib/mysql'

"""===基本程序==="""


def get_date_time(fm):
    """获取当前日期时间"""
    return time.strftime(fm, time.localtime(time.time()))


def time_diff(begin_time, end_time):
    """计算时间差"""
    seconds = (end_time - begin_time).seconds
    if seconds < 60:
        return str(seconds) + '秒'
    elif seconds >= 60 and seconds < 3600:
        m, s = divmod(seconds, 60)
        return str(m) + '分' + str(s) + '秒'
    else:
        h, s1 = divmod(seconds, 3600)
        if s1 >= 60:
            m, s2 = divmod(s1, 60)
            s = s2
        else:
            m = 0
            s = s1
        return str(h) + '小时' + str(m) + '分' + str(s) + '秒'


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


def gen_file(file_name, content):
    """生成文件"""
    with open(file_name, 'w') as f:
        f.write(content)
        return file_name


def read_file(file_name):
    """读取文件"""
    with open(file_name, 'r') as f:
        return f.read()


def gen_dir(dir_name):
    """生成目录"""
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
    return dir_name


def clean_file(file_name):
    """清理文件"""
    if os.path.isfile(file_name):
        os.remove(file_name)
        return file_name


def clean_dir(dir_name):
    """清理目录"""
    if os.path.isdir(dir_name):
        shutil.rmtree(dir_name)
        return dir_name


def tar_compress(dir_name):
    """使用tar压缩归档整个目录"""
    fm = '%Y%m%d_%H%M%S'
    tar_file_name = '{}_{}.tar.gz'.format(dir_name, get_date_time(fm))
    cmd = 'tar -zcf {} {}'.format(tar_file_name, dir_name)
    rc = os.system(cmd)
    if rc == 0:
        clean_dir(dir_name)
        return tar_file_name


def gzip_compress(file_name):
    """使用gzip压缩单个文件"""
    cmd = 'gzip -f9 {}'.format(file_name)
    rc = os.system(cmd)
    if rc == 0:
        return file_name + '.gz'


def get_file_size(file_name):
    """获取文件大小"""
    if os.path.isfile(file_name):
        return size_conversion(os.path.getsize(file_name))


def sync_file(file_name):
    """同步文件至远程主机"""
    cmd = 'rsync -qaP --rsh=ssh {} {}:{}/'.format(
        file_name, remote_host, remote_path)
    rc = os.system(cmd)
    if rc == 0:
        return file_name


def get_cmd_output(cmd):
    """获取Shell命令输出，过滤空字符串并以列表返回"""
    process = os.popen(cmd)
    output = process.read()
    process.close()
    return output


"""===主程序==="""


def main():
    """备份单个二进制日志文件"""
    print('***备份开始***')
    print('开始时间：' + get_date_time('%Y-%m-%d %H:%M:%S'))
    begin_time = datetime.datetime.now()
    # 获取上次备份记录的二进制日志文件
    last_binlog = read_file('last_binlog').strip().split()[0]
    # 获取当前二进制日志文件
    cmd = "mysql -BN -e 'show master status' | cut -f1"
    master_status = get_cmd_output(cmd).strip().split()[0]
    # 如果日志文件没有刷新过，则进行刷新并备份
    if master_status == last_binlog:
        # 刷新日志
        cmd = 'mysqladmin flush-logs'
        rc = os.system(cmd)
        if rc == 0:
            # 备份日志
            file_fullname = os.path.join(binlog_path, last_binlog)
            backup_name = '{}.{}'.format(
                last_binlog, get_date_time('%Y%m%d%H%M%S'))
            backup_fullname = os.path.join(backup_path, backup_name)
            cmd = 'rsync -qaP {} {}'.format(file_fullname, backup_fullname)
            rc = os.system(cmd)
            if rc == 0:
                # 压缩日志
                gzfile_fullname = gzip_compress(backup_fullname)
                print('备份文件：' + gzfile_fullname)
                print('文件大小：' + get_file_size(gzfile_fullname))
                # 记录最新的二进制日志文件，用于下次备份
                cmd = "mysql -BN -e 'show master status'"
                gen_file('last_binlog', get_cmd_output(cmd))
    else:
        print('服务器二进制日志异常')
    print('结束时间：' + get_date_time('%Y-%m-%d %H:%M:%S'))
    end_time = datetime.datetime.now()
    print('备份耗时：' + time_diff(begin_time, end_time))
    if os.path.isfile(gzfile_fullname):
        print('***同步文件***')
        print('同步文件：' + sync_file(gzfile_fullname))
        print('远程主机：' + remote_host)
        print('远程目录：' + remote_path)
    print('***备份结束***')


if __name__ == "__main__":
    main()
