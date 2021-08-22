#!/bin/bash
#
# 脚本名：vms_convert.sh
#
# 功能：此脚本用于将VMware虚拟机的.vmx格式配置文件和.vmdk格式磁盘镜像文件转换为Libvirt可以识别的.xml格式配置文件和.qcow2格式磁盘镜像文件
#
# 作者：Varden
#
# Start
echo "Start!"
echo

# 设定文件目录，默认为当前目录
echo "设定文件目录，默认为当前目录!"
VMX_DIR=.
XML_DIR=.
VMDK_DIR=.
QCOW2_DIR=.
echo;echo

# 转换.vmx格式配置文件
echo "转换.vmx格式配置文件!"
ls $VMX_DIR/*.vmx
echo
if [ $? == 0 ];then
    for I in `ls $VMX_DIR/*.vmx`;do
        # 去除文件名后缀
        F_NAME=`echo $I | awk -F / '{print $NF}' | awk -F . '{print $1}'`
        # 转换文件
        vmware2libvirt -f $I > $XML_DIR/$F_NAME.xml
        echo $I"文件转换成功!"
    done
else
    echo "错误! 没有找到.vmx格式配置文件!"
fi
echo;echo

# 转换.vmdk格式磁盘镜像文件
echo "转换.vmdk格式磁盘镜像文件!"
ls $VMDK_DIR/*.vmdk
echo
if [ $? == 0 ];then
    for I in `ls $VMDK_DIR/*.vmdk`;do
        # 去除文件名后缀
        F_NAME=`echo $I | awk -F / '{print $NF}' | awk -F . '{print $1}'`
        # 转换文件
        qemu-img convert -f vmdk -O qcow2 $I $QCOW2_DIR/$F_NAME.qcow2
        echo $I"文件转换成功!"
    done
else
    echo "错误! 没有找到.qcow2格式磁盘镜像文件!"
fi
echo

# End
echo "End!"
