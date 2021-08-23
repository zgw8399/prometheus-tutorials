#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# --------------------
# 描述：MySQL数据库增量备份
# 作者：Varden
# --------------------
#
from __future__ import print_function

import os
import os.path
import sys
import time
import datetime
import shutil

import json
import requests
import urllib3
import pymongo

# 禁用urllib3警告
urllib3.disable_warnings()

"""===企业微信环境==="""

# 消息主题
subject = 'MySQL数据库增量备份'
# 用户账号
user = ''
# 企业号的标识
corp_id = 'xxxxxxxxxxxxxxxx'
# 管理组凭证密钥
secret = 'xxxxxxxxxx-xxxxxxxxxxxxxxxxxxxx'
# 通讯录标签ID
tag_id = ''
# 应用ID
agent_id = '1000002'
# 部门ID
party_id = '2'

"""===备份环境==="""

# 备份主机
backup_host = '127.0.0.1'
# 本地备份路径
backup_path = '/data/backups'
# 远程主机
remote_host = 'varden.host'
# 远程备份路径
remote_path = '/remote/backups'
# mysql数据目录
mysql_datadir = '/var/lib/mysql'

"""===消息推送==="""


def get_token():
    """从微信服务器获取Token"""
    gettoken_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    data = {
        "corpid": corp_id,
        "corpsecret": secret
    }
    r = requests.get(url=gettoken_url, params=data, verify=False)
    if r.json()['errcode'] == 0:
        token = r.json()['access_token']
        return token
    else:
        return False


def send_message(subject, content):
    """发送消息"""
    token = get_token()
    if token:
        send_url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(
            token)
        data = {
            # 企业号中的用户帐号，在zabbix用户Media中配置，如果配置不正常，将按部门发送
            "touser": user,
            # 企业号中的标签id，群发使用（推荐）
            # "totag": tag_id,
            # 企业号中的部门id，群发时使用
            "toparty": party_id,
            # 消息类型
            "msgtype": "markdown",
            # 企业号中的应用id
            "agentid": agent_id,
            # 消息内容
            "markdown": {
                "content": """{subject}
                > **备份详情**
                > 开始时间：{begin_datetime}
                > 最新备份：{last_backup}
                > 备份大小：{backup_size}
                > 备份主机：{backup_host}
                > 备份路径：{backup_path}
                > 结束时间：{end_datetime}
                > 备份耗时：{backup_time}""".format(
                    subject=subject,
                    begin_datetime=content['begin_datetime'],
                    last_backup=content['last_backup'],
                    backup_size=content['backup_size'],
                    backup_host=content['backup_host'],
                    backup_path=content['backup_path'],
                    end_datetime=content['end_datetime'],
                    backup_time=content['backup_time'])
            },
            "safe": "0"
        }
        # 发送消息，失败则重试三次
        # json.dumps()是将dict转化成str格式
        r = requests.post(url=send_url, data=json.dumps(data), verify=False)
        count = 0
        while r.json()['errcode'] != 0 and count < 4:
            r = requests.post(
                url=send_url, data=json.dumps(data), verify=False)
            count += 1
        return '消息发送状态：' + r.json()['errmsg']
    else:
        return '获取Token失败'


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
    tar_file_name = '{}.tar.gz'.format(dir_name)
    cmd = 'tar -zcf {} {}'.format(tar_file_name, dir_name)
    rc = os.system(cmd)
    if rc == 0:
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
    cmd = 'rsync -aP --rsh=ssh {} {}:{}/'.format(
        file_name, remote_host, remote_path)
    rc = os.system(cmd)
    if rc == 0:
        print('---同步成功---')
    else:
        print('---同步失败---')


def sync_dir(local_path, remote_path, remote_host):
    """同步目录所有文件至远程"""
    cmd = 'rsync -aP --rsh=ssh {}/ {}:{}/'.format(
        local_path, remote_host, remote_path)
    print('---同步信息---')
    rc = os.system(cmd)
    if rc == 0:
        print('---同步成功---')
    else:
        print('---同步失败---')


def get_cmd_output(cmd):
    """获取Shell命令输出，过滤空字符串并以列表返回"""
    process = os.popen(cmd)
    output = process.read()
    process.close()
    return output


def read_file(file_name):
    """读取文件"""
    with open(file_name, 'r') as f:
        return f.read()


"""===主程序==="""


def main():
    """xtrabackup增量备份"""
    # 获取上一次备份
    last_backup_filename = os.path.join(backup_path, 'last_backup')
    if os.path.isfile(last_backup_filename):
        last_backup = read_file(last_backup_filename).strip().split()[0]
        incr_basedir = os.path.join(backup_path, last_backup)
        if os.path.isdir(incr_basedir):
            print('***备份开始***')
            print('上次备份：' + incr_basedir)
            begin_datetime = get_date_time('%Y-%m-%d %H:%M:%S')
            print('开始时间：' + begin_datetime)
            begin_time = datetime.datetime.now()
            date_time = get_date_time('%Y%m%d_%H%M%S')
            dir_name = 'incr_{}'.format(date_time)
            dir_fullname = os.path.join(backup_path, dir_name)
            cmd = 'xtrabackup --backup --target-dir={} --incremental-basedir={} --datadir={}/'.format(
                gen_dir(dir_fullname), incr_basedir, mysql_datadir)
            print('---备份信息---')
            rc = os.system(cmd)
            if rc == 0:
                # 记录最新备份，用于增量备份
                gen_file(last_backup_filename, dir_name)
                print('---压缩归档---')
                tarfile_fullname = tar_compress(dir_fullname)
                print('---备份成功---')
                print('备份文件：' + tarfile_fullname)
                backup_size = get_file_size(tarfile_fullname)
                print('文件大小：' + backup_size)
            else:
                print('---备份失败---')
            print('***同步文件***')
            sync_file(tarfile_fullname)
            print('远程主机：' + remote_host)
            print('远程目录：' + remote_path)
            end_datetime = get_date_time('%Y-%m-%d %H:%M:%S')
            print('结束时间：' + end_datetime)
            end_time = datetime.datetime.now()
            backup_time = time_diff(begin_time, end_time)
            print('备份耗时：' + backup_time)
            print('***备份结束***')
            print('***推送微信消息***')
            content = {
                "begin_datetime": begin_datetime,
                "last_backup": tarfile_fullname,
                "backup_size": backup_size,
                "backup_host": backup_host,
                "backup_path": backup_path,
                "end_datetime": end_datetime,
                "backup_time": backup_time
            }
            status = send_message(subject, content)
            print(status)
        else:
            print('上一次备份不存在')
    else:
        print('记录最新备份的文件不存在')


if __name__ == "__main__":
    main()
