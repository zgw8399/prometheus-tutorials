#!/bin/bash
#
echo "### Cluster Status ###"
ceph -s
echo "### Ceph DF Detail ###"
ceph df detail
echo "### OSD DF(%) Detail###"
ceph osd df | awk '{print $7}' | grep -v USE | grep -v '^$' | sort -rn | head -10
echo "### OSD Perf Detail###"
ceph osd perf
