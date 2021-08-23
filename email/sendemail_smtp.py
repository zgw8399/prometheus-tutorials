#!/usr/bin/python3
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

"""第三方 SMTP 服务"""
# 设置服务器
mail_host = 'smtp.xx.com'
# 设置服务器端口
mail_port = '25'
# 用户名
mail_user = 'xxxxx'
# 口令
mail_pass = 'xxxxxx'

# 发件人邮箱
sender = 'xxxxx@xx.com'
# 接收人邮箱
receivers = ['yyyyy@xx.com', 'zzzzz@xx.com']


def mail(subject, content):
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header(sender, 'utf-8')
    message['To'] = Header(','.join(receivers), 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, mail_port)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


if __name__ == '__main__':
    subject = 'Python3 SMTP 邮件测试'
    content = 'Python3 邮件发送测试...'
    mail(subject, content)
