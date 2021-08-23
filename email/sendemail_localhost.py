#!/usr/bin/python3
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 发送邮箱
sender = 'root@varden.host'
# 接收邮箱
receivers = ['xx@163.com']


def mail(subject, content):
    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText(content, 'plain', 'utf-8')
    # 发送者
    message['From'] = Header(sender, 'utf-8')
    # 接收者
    message['To'] = Header(','.join(receivers), 'utf-8')
    # 邮件主题
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


if __name__ == '__main__':
    subject = 'Sendmail邮件测试'
    content = 'Python邮件发送测试...'
    mail(subject, content)
