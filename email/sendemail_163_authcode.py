#!/usr/bin/python3
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# 发件人邮箱昵称
sender_nickname = 'varden.host'
# 发件人邮箱账号
sender = 'xx@163.com'
# 发件人邮箱授权码
sender_authcode = 'xxxxx'
# 收件人昵称
receiver_nickname = 'Varden'
# 收件人邮箱账号
receiver = 'xx@163.com'
# SMTP服务器
smtp_server = 'smtp.163.com'
# SMTP端口
smtp_port = '465'


def mail(subject, content):
    ret = True
    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        # 括号里的对应发件人邮箱昵称、账号
        msg['From'] = formataddr([sender_nickname, sender])
        # 括号里的对应收件人邮箱昵称、账号
        msg['To'] = formataddr([receiver_nickname, receiver])
        # 邮件的主题
        msg['Subject'] = subject

        # 发件人邮箱中的SMTP服务器、端口
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        # 括号中对应的是发件人邮箱账号、授权码
        server.login(sender, sender_authcode)
        # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.sendmail(sender, [receiver, ], msg.as_string())
        # 关闭连接
        server.quit()
    # 如果 try 中的语句没有执行，则会执行下面的 ret=False
    except Exception:
        ret = False
    return ret


if __name__ == '__main__':
    subject = '163邮箱授权码测试'
    content = '邮件内容'
    ret = mail(subject, content)
    if ret:
        print("邮件发送成功")
    else:
        print("邮件发送失败")
