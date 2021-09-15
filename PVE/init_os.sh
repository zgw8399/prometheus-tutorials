#!/bin/bash
#
# 脚本名：init_os.sh
#
# 描述：
#   - 注意：重复执行此脚本是幂等的
#   - 此脚本用于初始化配置 Debian 操作系统，并安装配置所需软件
#   - 执行此脚本之前必须保持外网网络畅通，否则无法更新系统和安装软件
#   - 运行脚本时，建议使用 tee 命令将输出结果保存一份至日志文件，以便之后排查问题，例如执行：./init_os.sh | tee init_os.log
#
# 作者：Varden
#
## 脚本开始

set -u

echo "***获取Debian发行版代号***"
CODE_NAME=`lsb_release -sc`
echo ${CODE_NAME}

echo "***指定安装的Ceph发行版代号***"
CEPH_CODENAME=pacific
echo ${CEPH_CODENAME}

## 添加存储库并更新配置系统

echo "***添加Debian存储库***"
cat << EOF > /etc/apt/sources.list
deb http://mirrors.ustc.edu.cn/debian ${CODE_NAME} main contrib non-free
deb http://mirrors.ustc.edu.cn/debian ${CODE_NAME}-updates main contrib non-free
deb http://mirrors.ustc.edu.cn/debian-security/ ${CODE_NAME}-security main non-free contrib
EOF
cat /etc/apt/sources.list

echo "***添加Proxmox VE存储库密钥***"
if [ ! -e /etc/apt/trusted.gpg.d/proxmox-release-${CODE_NAME}.gpg ];then
    wget https://enterprise.proxmox.com/debian/proxmox-release-${CODE_NAME}.gpg -O /etc/apt/trusted.gpg.d/proxmox-release-${CODE_NAME}.gpg
    echo "密钥已下载"
else
    echo "密钥已存在"
fi

echo "***添加Proxmox VE存储库***"
echo "deb http://mirrors.ustc.edu.cn/proxmox/debian ${CODE_NAME} pve-no-subscription" | tee /etc/apt/sources.list.d/pve-no-subscription.list
if [ -e /etc/apt/sources.list.d/pve-enterprise.list ];then
    rm -f /etc/apt/sources.list.d/pve-enterprise.list
fi

echo "***添加Ceph存储库***"
echo "deb http://mirrors.ustc.edu.cn/proxmox/debian/ceph-${CEPH_CODENAME}/ ${CODE_NAME} main" | tee /etc/apt/sources.list.d/ceph_mirror.list

echo "***更新系统***"
apt update
apt -y upgrade

echo "***安装常用工具***"
apt install -y net-tools tree vim wget curl apt-transport-https chrony

echo "***修改时区***"
timedatectl set-timezone Asia/Shanghai
timedatectl

## 安装Proxmox VE

echo "***安装Proxmox VE***"
apt install -y proxmox-ve postfix open-iscsi

## 安装Ceph

echo "***安装Ceph***"
echo 'y' | pveceph install --version ${CEPH_CODENAME}

## 移除旧安装包

echo "***移除旧安装包***"
apt autoremove -y

## 脚本结束

