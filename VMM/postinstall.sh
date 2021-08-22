#!/bin/sh
#
PXESERVER=10.10.10.10

# Get firstboot script.
/usr/bin/wget -O /root/firstboot.sh http://${PXESERVER}/pxe/firstboot.sh
chmod +x /root/firstboot.sh

# Create a service that will run firstboot.sh script.
cat >/etc/init.d/firstboot << EOF
#! /bin/sh
#
### BEGIN INIT INFO
# Provides:        firstboot
# Required-Start:  \$networking
# Required-Stop:   \$networking
# Default-Start:   2 3 4 5
# Default-Stop:    0 1 6
# Short-Description: A script that runs once
# Description: A script that runs once
### END INIT INFO
cd /root; /usr/bin/nohup sh -x /root/firstboot.sh &
EOF

# Install the firstboot service.
chmod +x /etc/init.d/firstboot
update-rc.d firstboot defaults
echo "Finished postinstall"

# End
