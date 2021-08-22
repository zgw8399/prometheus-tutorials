#!/bin/bash
#
# ----------
# 脚本名称：install_mongodb.sh
# 脚本功能：安装配置MongoDB服务器
# ----------
#
set -u

# ===设定环境变量===

echo "===安装MongoDB==="
dpkg -l mongodb-org &>/dev/null
RETVAL=$?
if [ ! $RETVAL -eq 0 ];then
	wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add -
	echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.4 main" | tee /etc/apt/sources.list.d/mongodb-org-4.4.list
	apt-get update
	apt-get install -y mongodb-org
	apt-mark hold mongodb-org mongodb-org-server mongodb-org-shell mongodb-org-mongos mongodb-org-tools
	echo "MongoDB安装完毕！"
else
	echo "MongoDB已安装！"
fi

echo "===启动MongoDB服务==="
/usr/bin/killall -0 mongod &>/dev/null
RETVAL=$?
if [ ! $RETVAL -eq 0 ];then
	/usr/bin/systemctl start mongod.service
	/usr/bin/systemctl status mongod.service
	/usr/bin/systemctl enable mongod.service
	echo "服务已启动！"
else
	echo "服务已运行！"
	/usr/bin/systemctl status mongod.service
fi

# ===脚本结束===
