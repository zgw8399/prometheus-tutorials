#!/bin/bash
#
# --------------------
# 脚本名称：revoke_client.sh
# 脚本功能：此脚本将使用命令行第一个参数作为客户端识别码，吊销客户端证书并删除客户端配置文件
# --------------------
#
set -u

# ===设定变量===

# 设定证书和密钥所在目录
KEY_DIR=/usr/share/easy-rsa
# 设定客户端配置文件所在目录
OUTPUT_DIR=~/openvpn-scripts/files
# CCD configs
CCD_DIR=/etc/openvpn/ccd

echo "===吊销客户端证书和密钥对==="
if [ -e $KEY_DIR/pki/issued/$1.crt ];then
	cd $KEY_DIR
	echo 'yes' | ./easyrsa revoke $1
    ./easyrsa gen-crl
    cp $KEY_DIR/pki/crl.pem /etc/openvpn/
	echo "客户端证书和密钥对已吊销！"
else
	echo "客户端证书和密钥对不存在！"
fi

echo "===删除客户端配置文件==="
if [ -e $OUTPUT_DIR/$1.ovpn ];then
    rm -f $OUTPUT_DIR/$1.ovpn
    rm -f $CCD/$1
	echo "客户端配置文件已删除！"
else
	echo "客户端配置文件不存在！"
fi

# ===脚本结束===
