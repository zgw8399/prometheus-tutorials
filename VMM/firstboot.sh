#!/bin/sh
#
# This script will run the first time the system boots. Even
# though we've told it to run after networking is enabled,
#
# Introducing a brief sleep makes things work right all the
# time. The time for DHCP to catch up.
sleep 90

# Install new sources.
cat << EOF >/etc/apt/sources.list
deb http://10.10.10.10/debian/ stretch main contrib non-free
EOF

# Update system and install some softwares.
apt-get update
apt-get -y upgrade
apt-get -y install python sudo bridge-utils vlan

# Configure ssh.
sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
sed -i 's/#UseDNS no/UseDNS no/g' /etc/ssh/sshd_config

# Configure sudo privileges for test user.
echo "test ALL = (root) ALL" | tee /etc/sudoers.d/test
chmod 0440 /etc/sudoers.d/test

# Create testceph user.
useradd -d /home/testceph -m testceph
echo testceph:testceph | chpasswd

echo "testceph ALL = (root) NOPASSWD:ALL" | tee /etc/sudoers.d/testceph
chmod 0440 /etc/sudoers.d/testceph

# Modify timezone.
echo "Asia/Shanghai" | tee /etc/timezone

# Delete some services.
update-rc.d firstboot remove
update-rc.d exim4 remove
update-rc.d nfs-common remove
update-rc.d rpcbind remove
rm /etc/init.d/firstboot /root/firstboot

# Configure iptables.
iptables -Z
iptables -F
iptables -X

# Reboot system.
/sbin/reboot

# End
