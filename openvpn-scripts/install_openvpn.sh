#!/bin/bash
#
# ----------
# 脚本名称：install_openvpn.sh
# 脚本功能：安装配置OpenVPN服务器
# ----------
#
set -u

# ===设定环境变量===
EASYRSA_DIR=/usr/share/easy-rsa
OPENVPN_CONFIG_DIR=/etc/openvpn
SCRIPT_DIR=~/openvpn-scripts

echo "===安装OpenVPN==="
dpkg -l openvpn &>/dev/null
RETVAL=$?
if [ ! $RETVAL -eq 0 ];then
	apt-get install -y openvpn openssl libssl-dev lzop psmisc
	apt-mark hold openvpn
	echo "OpenVPN安装完毕！"
else
	echo "OpenVPN已安装！"
fi

echo "===安装EasyRSA==="
dpkg -l easy-rsa &>/dev/null
RETVAL=$?
if [ ! $RETVAL -eq 0 ];then
	apt-get install -y easy-rsa
	apt-mark hold easy-rsa
	echo "EasyRSA安装完毕！"
else
	echo "EasyRSA已安装！"
fi

echo "===配置EasyRSA变量==="
if [ ! -e $EASYRSA_DIR/vars ];then
	cp $EASYRSA_DIR/vars.example $EASYRSA_DIR/vars
	echo -n "set_var EASYRSA_REQ_COUNTRY   \"CN\"
set_var EASYRSA_REQ_PROVINCE  \"Guangdong\"
set_var EASYRSA_REQ_CITY      \"Shenzhen\"
set_var EASYRSA_REQ_ORG       \"Varden\"
set_var EASYRSA_REQ_EMAIL     \"varden@qq.com\"
set_var EASYRSA_REQ_OU        \"Varden\"
">>$EASYRSA_DIR/vars
	echo "变量文件已生成！"
else
	echo "变量文件已存在！"
fi

echo "===构建CA==="
if [ ! -d $EASYRSA_DIR/pki ];then
	cd $EASYRSA_DIR
	./easyrsa init-pki
	echo "PKI初始化完毕！"
else
	echo "PKI已初始化！"
fi

if [ ! -e $EASYRSA_DIR/pki/ca.crt ];then
	cd $EASYRSA_DIR
	echo "openvpn" | ./easyrsa build-ca nopass
	echo "CA证书已生成！"
else
	echo "CA证书已存在！"
fi

echo "===构建服务器证书==="
if [ ! -e $EASYRSA_DIR/pki/reqs/server.req ];then
	cd $EASYRSA_DIR
	echo "server" | ./easyrsa gen-req server nopass
	echo "认证请求文件已生成！"
else
	echo "认证请求文件已存在！"
fi

if [ ! -e $EASYRSA_DIR/pki/issued/server.crt ];then
	cd $EASYRSA_DIR
	echo "yes" | ./easyrsa sign-req server server
	echo "签署服务器证书成功！"
else
	echo "服务器证书已签署！"
fi

echo "===创建Diffie-Hellman密钥==="
if [ ! -e $EASYRSA_DIR/pki/dh.pem ];then
	cd $EASYRSA_DIR
	./easyrsa gen-dh
	echo "DH密钥已生成！"
else
	echo "DH密钥已存在！"
fi

echo "===生成HMAC签名以增强服务器的TLS完整性验证功能==="
if [ ! -e $EASYRSA_DIR/ta.key ];then
	cd $EASYRSA_DIR
	openvpn --genkey --secret ta.key
	echo "HMAC签名已生成！"
else
	echo "HMAC签名已存在！"
fi

echo "===准备服务器所需的所有证书和密钥文件==="
if [ ! -e $OPENVPN_CONFIG_DIR/ca.crt ];then
	cp $EASYRSA_DIR/pki/ca.crt $OPENVPN_CONFIG_DIR/
	echo "CA公钥已复制！"
else
	echo "CA公钥已存在！"
fi

if [ ! -e $OPENVPN_CONFIG_DIR/server.key ];then
	cp $EASYRSA_DIR/pki/private/server.key $OPENVPN_CONFIG_DIR/
	echo "服务器私钥已复制！"
else
	echo "服务器私钥已存在！"
fi

if [ ! -e $OPENVPN_CONFIG_DIR/server.crt ];then
	cp $EASYRSA_DIR/pki/issued/server.crt $OPENVPN_CONFIG_DIR/
	echo "服务器公钥已复制！"
else
	echo "服务器公钥已存在！"
fi

if [ ! -e $OPENVPN_CONFIG_DIR/dh.pem ];then
	cp $EASYRSA_DIR/pki/dh.pem $OPENVPN_CONFIG_DIR/
	echo "DH密钥已复制！"
else
	echo "DH密钥已存在！"
fi

if [ ! -e $OPENVPN_CONFIG_DIR/ta.key ];then
	cp $EASYRSA_DIR/ta.key $OPENVPN_CONFIG_DIR/
	echo "HMAC签名已复制！"
else
	echo "HMAC签名已存在！"
fi

echo "===准备服务器配置文件==="
if [ ! -e $OPENVPN_CONFIG_DIR/server.conf ];then
	cat $SCRIPT_DIR/server_base.conf > $OPENVPN_CONFIG_DIR/server.conf
	echo "配置文件已生成！"
else
	echo "配置文件已存在！"
fi
sed -i 's/#AUTOSTART="home office"/AUTOSTART="server"/' /etc/default/openvpn

echo "===调整服务器网络配置==="
echo "net.ipv4.ip_forward=1" | tee /etc/sysctl.d/openvpn.conf
sysctl -p

echo "===启动OpenVPN服务==="
/usr/bin/killall -0 openvpn &>/dev/null
RETVAL=$?
if [ ! $RETVAL -eq 0 ];then
	/usr/bin/systemctl start openvpn@server
	/usr/bin/systemctl status openvpn@server
	/usr/bin/systemctl enable openvpn@server
	echo "服务已启动！"
else
	echo "服务已运行！"
	/usr/bin/systemctl status openvpn@server
fi

# ===脚本结束===
