#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
import sys
import json
import requests

import time
import hmac
import hashlib
import base64
import urllib
import urllib3

# 禁用urllib3警告
urllib3.disable_warnings()


def make_sign(timestamp, secret):
    """签名计算"""
    # 新版钉钉更新了安全策略，这里我们采用签名的方式进行安全认证。钉钉开发文档地址如下：
    # https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq
    secret_enc = bytes(secret, 'utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = bytes(string_to_sign, 'utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc,
                         digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign


def send_message(token, secret, subject, content):
    """发送消息"""
    timestamp = int(round(time.time() * 1000))
    url = 'https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}'.format(
        token, timestamp, make_sign(timestamp, secret))
    data = {
        "msgtype": "text",
        "text": {
            "content": subject + "\n\n" + content
        }
    }
    r = requests.post(url, json=data)
    count = 0
    while r.json()['errcode'] != 0 and count < 4:
        r = requests.post(url, json=data)
        count += 1
    return '消息发送状态：' + r.json()['errmsg']


if __name__ == '__main__':
    token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    subject = str(sys.argv[1])
    content = str(sys.argv[2])
    status = send_message(token, secret, subject, content)
    print(status)
