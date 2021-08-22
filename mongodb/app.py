#!/usr/bin/python
# -*- coding:utf-8 -*-
#
# --------------------
# 脚本名称：app.py
# 配置文件：config/wechat.conf
# 脚本描述：此脚本用于发送消息至指定的企业微信群。运行脚本之前，请修改配置文件。
# 作者：Varden
# --------------------
#
import requests
import os
import sys
import json
import urllib3
import ConfigParser

from commands import getstatusoutput
from commands import getoutput

# 禁用urllib3警告
urllib3.disable_warnings()

# 设置python的默认编码，一般设置为utf8的编码格式
reload(sys)
sys.setdefaultencoding('utf-8')


"""从微信服务器获取Token的函数"""
def GetTokenFromServer(Corpid,Secret):
    Url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    Data = {
        "corpid":Corpid,
        "corpsecret":Secret
    }
    r = requests.get(url=Url,params=Data,verify=False)
    # 输出获取的原始数据。
    print(r.json())
    if r.json()['errcode'] != 0:
        return False
    else:
        Token = r.json()['access_token']
        return Token


"""发送消息的函数"""
def SendMessage(User,Agentid,Subject,Content):
    Token = GetTokenFromServer(Corpid, Secret)
    Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % Token
    Data = {
        # 企业号中的用户帐号，在zabbix用户Media中配置，如果配置不正常，将按部门发送
        "touser": User,
        # 企业号中的标签id，群发使用（推荐）
        #"totag": Tagid,
        # 企业号中的部门id，群发时使用
        "toparty": Partyid,
        # 消息类型
        "msgtype": "text",
        # 企业号中的应用id
        "agentid": Agentid,
        "text": {
            "content": Subject + '\n' + '===报告信息===' + '\n' + Content
        },
        "safe": "0"
    }
    # json.dumps()是将dict转化成str格式
    r = requests.post(url=Url,data=json.dumps(Data),verify=False)
    # 如果发送消息失败，则重试三次
    n = 0
    while r.json()['errcode'] != 0 and n < 4:
        n+=1
        Token = GetTokenFromServer(Corpid, Secret)
        if Token:
            Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % Token
            r = requests.post(url=Url,data=json.dumps(Data),verify=False)
    return r.json()


if __name__ == '__main__':
    # 读取配置文件
    cf = ConfigParser.ConfigParser()
    cf.read("./config/wechat.conf")
    # 获取用户账号
    User = cf.get("wechat", "user")
    # 获取消息主题
    Subject = cf.get("wechat", "subject")
    # 获取消息内容
    Content = getoutput('./backup.sh')
    # 获取企业号的标识
    Corpid = cf.get("wechat", "corpid")
    # 获取管理组凭证密钥
    Secret = cf.get("wechat", "secret")
    # 获取通讯录标签ID
    #Tagid = cf.get("wechat", "tagid")
    # 获取应用ID
    Agentid = cf.get("wechat", "agentid")
    # 获取部门ID
    Partyid = cf.get("wechat", "partyid")
    # 调用函数发送消息
    Status = SendMessage(User,Agentid,Subject,Content)
    print Status
