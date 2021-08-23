#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# --------------------
# 描述：此脚本用于发送消息至指定的企业微信群
# 作者：Varden
# --------------------
#
import os
import sys
import json
import requests
import urllib3

# 禁用urllib3警告
urllib3.disable_warnings()

"""企业微信"""

# 用户账号
user = ''
# 企业号的标识
corp_id = 'xxxxxxxxxxxx'
# 管理组凭证密钥
secret = 'xxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxx'
# 通讯录标签ID
tag_id = ''
# 应用ID
agent_id = '1000002'
# 部门ID
party_id = '2'


"""消息推送"""


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
                "content": """{}
                > **消息详情**
                > 内容：{}""".format(subject, content)
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


if __name__ == '__main__':
    subject = '测试主题'
    content = '这是一条测试消息'
    status = send_message(subject, content)
    print(status)
