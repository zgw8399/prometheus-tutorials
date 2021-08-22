#!/bin/bash
#
#  脚本名：add_vlan_br.sh
#  脚本描述：此脚本实现安装配置linux系统vlan及桥
#
### 安装软件包
apt-get update
apt-get install -y vlan bridge-utils

### 加载模块
modprobe 8021q
echo "8021q" >>/etc/modules
lsmod | grep 8021

### 测试创建vlan接口及桥
for VLAN_ID in 33 40 47 999 3018;do
    vconfig add eno1 $VLAN_ID
    brctl addbr br$VLAN_ID
    brctl addif br$VLAN_ID eno1.$VLAN_ID
done

### 检查配置
ip add | grep eno1
brctl show

cat <<EOF >>/etc/network/interfaces
### vlan

auto eno1.33
iface eno1.33 inet static
vlan-raw-device eno1

auto eno1.40
iface eno1.40 inet static
vlan-raw-device eno1

auto eno1.47  
iface eno1.47 inet static  
vlan-raw-device eno1

auto eno1.999  
iface eno1.999 inet static  
vlan-raw-device eno1

auto eno1.3018  
iface eno1.3018 inet static  
vlan-raw-device eno1

### br

auto br33
iface br33 inet static
bridge_ports eno1.33

auto br40
iface br40 inet static
bridge_ports eno1.40

auto br47
iface br47 inet static
bridge_ports eno1.47
address 10.10.10.12
netmask 255.255.252.0
gateway 10.10.11.253

auto br999
iface br999 inet static
bridge_ports eno1.999

auto br3018
iface br3018 inet static
bridge_ports eno1.3018

### storage

auto eno2d1
iface eno2d1 inet static
address 10.0.0.11
netmask 255.255.255.0
EOF

### end
