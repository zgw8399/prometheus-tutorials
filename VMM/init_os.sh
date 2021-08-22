#!/bin/bash
#
# 脚本名：init_os.sh
# 描述：
#   - 注意：不要重复执行此脚本
#   - 此脚本用于初始化配置Debian stretch操作系统，并安装配置常用软件
#   - 执行此脚本之前必须保持外网网络畅通，否则无法更新系统和安装软件
#   - 运行脚本时，建议使用tee命令将输出结果保存一份至文件，以便之后排查问题，例如：./init_os.sh | tee init_os.log
#
#
## Start
echo "开始安装!---------------------------------------------------------------------------"

# 安装通用软件
echo "安装通用软件!"
apt-get -y update
apt-get -y install net-tools python vim wget apt-transport-https sysv-rc-conf nano emacs iftop tcpdump

# 添加ceph源，版本为 jewel-10.2.z
echo "添加ceph源!"
wget -q -O- 'https://download.ceph.com/keys/release.asc' | apt-key add -
echo deb https://download.ceph.com/debian-jewel/ $(lsb_release -sc) main | tee /etc/apt/sources.list.d/ceph.list
apt-get -y update

# 安装ceph-fuse
echo "安装ceph-fuse!"
apt-get -y install ceph-fuse

# 配置及监控ssh
mkdir -p /root/.ssh
echo "UseDNS no" >>/etc/ssh/sshd_config

# 安装配置ntp
echo "安装配置ntp!"
apt-get -y install chrony
sed -i 's/pool 2.debian.pool.ntp.org iburst/#pool 2.debian.pool.ntp.org iburst/g' /etc/chrony/chrony.conf
echo "server 192.168.0.200 iburst" >>/etc/chrony/chrony.conf
update-rc.d chrony defaults
/etc/init.d/chrony restart

# 添加部署用户并配置其sudo权限
echo "添加新用户并配置其sudo权限!"
apt-get -y install sudo
useradd -d /home/testceph -m testceph
echo testceph:testceph | chpasswd
echo "testceph ALL = (root) NOPASSWD:ALL" | tee /etc/sudoers.d/testceph
chmod 0440 /etc/sudoers.d/testceph

# 开启包转发
echo "开启包转发!"
echo 1 >/proc/net/ipv4/ip_forward
cat <<EOF >>/etc/sysctl.conf
net.ipv4.ip_forward=1
EOF
sysctl -p

# 修改时区
echo "修改时区!"
cat <<EOF >/etc/timezone
Asia/Shanghai
EOF

# 更新hosts
echo "更新hosts!"
cat <<EOF >/etc/hosts
127.0.0.1    localhost
EOF

# 安装虚拟化软件
echo "安装虚拟化软件!"
apt-get -y install qemu qemu-kvm libvirt-daemon-system libvirt-clients virtinst qemu-block-extra

# 清空防火墙
iptables -Z
iptables -F
iptables -X

## End
echo "安装完成!------------------------------------------------------------------------"
