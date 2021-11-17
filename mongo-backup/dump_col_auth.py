#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# --------------------
# 描述：备份MongoDB单个集合
# 作者：Varden
# --------------------
#
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
subject = 'MongoDB数据库备份'
# 用户账号
user = ''
# 企业号的标识
corp_id = ''
# 管理组凭证密钥
secret = ''
# 通讯录标签ID
tag_id = ''
# 应用ID
agent_id = '1000002'
# 部门ID
party_id = '2'

"""===备份环境==="""

# 数据库主机
db_host = ''
# 数据库端口
db_port = '27017'
# 数据库用户
db_user = ''
# 数据库密码
db_password = ''
# 备份主机
backup_host = ''
# 备份路径
backup_root_path = '/data/backups/mongodb'
# 备份保留数量
keep_num = 10


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
    cmd = 'rsync -aP --rsh=ssh {} {}:{}/'.format(
        file_name, remote_host, remote_path)
    rc = os.system(cmd)
    if rc == 0:
        clean_file(file_name)
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


"""===主程序==="""


def main(db_name, col_name):
    """单集合备份"""
    client = pymongo.MongoClient("mongodb://{}:{}@{}:{}/admin".format(db_user, db_password, db_host, db_port))
    db_list = client.list_database_names()
    if db_name in db_list:
        db = client[db_name]
        col_list = db.list_collection_names()
        if col_name in col_list:
            print('***备份开始***')
            begin_datetime = get_date_time('%Y-%m-%d %H:%M:%S')
            begin_time = datetime.datetime.now()
            print('开始时间：' + begin_datetime)
            db_backup_path = os.path.join(backup_root_path, db_name)
            backup_path = os.path.join(gen_dir(db_backup_path), col_name)
            file_name = '{}.{}.{}.gz'.format(db_name, col_name, get_date_time('%Y%m%d_%H%M%S'))
            file_fullname = os.path.join(gen_dir(backup_path), file_name)
            cmd = 'mongodump --host={} --port={} --username={} --password={} --authenticationDatabase=admin --archive={} --gzip --db={} --collection={}'.format(db_host, db_port, db_user, db_password, file_fullname, db_name, col_name)
            print('---备份信息---')
            rc = os.system(cmd)
            if rc == 0:
                backup_size = get_file_size(file_fullname)
                print('最新备份：' + file_name)
                print('备份大小：' + backup_size)
                print('备份主机：' + backup_host)
                print('备份路径：' + backup_path)
                print('---备份成功---')
            else:
                print('---备份失败---')
            end_datetime = get_date_time('%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.now()
            backup_time = time_diff(begin_time, end_time)
            print('结束时间：' + end_datetime)
            print('备份耗时：' + backup_time)
            print('***备份结束***')
            print('***清理历史备份***')
            del_files = clean_history_file(backup_path, keep_num)
            for del_file in del_files:
                print('清理文件：' + del_file)
            print('***推送微信消息***')
            content = {
                "begin_datetime": begin_datetime,
                "last_backup": file_name,
                "backup_size": backup_size,
                "backup_host": backup_host,
                "backup_path": backup_path,
                "end_datetime": end_datetime,
                "backup_time": backup_time
            }
            status = send_message(subject, content)
            print(status)
        else:
            print('`{}` collection not exists.'.format(col_name))
    else:
        print('`{}` database not exists.'.format(db_name))
    client.close()


if __name__ == "__main__":
    arg_list = sys.argv
    if len(arg_list) == 3:
        main(arg_list[1], arg_list[2])
    else:
        print('option error, please input `db_name` and `col_name` option.')
