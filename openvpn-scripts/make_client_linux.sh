#!/bin/bash
#
# --------------------
# 脚本名称：make_client.sh
# 脚本功能：此脚本将使用命令行第一个参数作为客户端识别码，并生成客户端配置文件
# --------------------
#
set -u

# ===设定变量===

# 设定证书和密钥所在目录
KEY_DIR=/usr/share/easy-rsa
# 设定生成的客户端配置文件所在目录
OUTPUT_DIR=~/openvpn-scripts/files
# 设定基本配置文件目录
BASE_CONFIG=~/openvpn-scripts/client_base_linux.conf

# ===创建目录===

if [ ! -d $OUTPUT_DIR ];then
	mkdir -p $OUTPUT_DIR
fi

echo "===生成客户端证书和密钥对==="
if [ ! -e $KEY_DIR/pki/issued/$1.crt ];then
	cd $KEY_DIR
	echo $1 | ./easyrsa gen-req $1 nopass
    echo 'yes' | ./easyrsa sign-req client $1
	echo "客户端证书和密钥对已生成！"
else
	echo "客户端证书和密钥对已存在！"
fi

echo "===生成客户端配置文件==="
if [ ! -e $OUTPUT_DIR/$1.ovpn ];then
	cat $BASE_CONFIG \
		<(echo -e '<ca>') \
		$KEY_DIR/pki/ca.crt \
		<(echo -e '</ca>\n<cert>') \
		$KEY_DIR/pki/issued/$1.crt \
		<(echo -e '</cert>\n<key>') \
		$KEY_DIR/pki/private/$1.key \
		<(echo -e '</key>\n<tls-auth>') \
		$KEY_DIR/ta.key \
		<(echo -e '</tls-auth>') \
		> $OUTPUT_DIR/$1.ovpn
	echo "客户端配置文件已生成！"
else
	echo "客户端配置文件已存在！"
fi

# ===脚本结束===
