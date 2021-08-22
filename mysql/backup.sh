#!/bin/bash
#
# --------------------
# 脚本名称：backup.sh
# 脚本描述：此脚本用于全量备份MySQL除系统外的所有数据库实例。运行脚本之前，请至少修改数据库相关变量值。
# 作者：Varden
# --------------------
#
# ===设定变量===

# 设定备份的数据库类型
DB_NAME=MySQL

# 设定数据库主机
DB_HOST=192.168.2.8

# 设定数据库端口
DB_PORT=3306

# 设定数据库用户
DB_USER=root

# 设定数据库密码
DB_PASSWORD=password

# 设定备份时间
BAK_TIME=`date '+%Y-%m-%d %H:%M'`

# 设定备份文件名
BAK_FILE=data-`date '+%Y%m%d%H%M'`.tar.gz

# 设定备份目录及临时目录
BAK_DIR=/var/backups/mysql
TMP_DIR=$BAK_DIR/tmp

# 设定备份程序
MYSQL_BIN=$(which mysql)
MYSQLDUMP_BIN=$(which mysqldump)

# 设定备份保留时间
BAK_KEEPTIME=60

# ===创建客户端配置文件

cat>~/.my.cnf<<EOF
[client]
port = $DB_PORT
user = $DB_USER
password = $DB_PASSWORD
default-character-set = utf8
EOF
chmod 0400 ~/.my.cnf

# ===创建相关目录===

if [ ! -d $TMP_DIR ]; then
    mkdir -p $TMP_DIR
fi

# ===导出数据===

DBS=`$MYSQL_BIN -h$DB_HOST -e 'show databases;' | awk '{print $1}' | grep -E -v '(information_schema|performance_schema|mysql|sys|Database)'`
for DB in $DBS;do
    $MYSQLDUMP_BIN -h$DB_HOST $DB >$TMP_DIR/$DB.sql
done

# ===压缩归档数据===

cd $TMP_DIR
tar -pzcf $BAK_DIR/$BAK_FILE . &>/dev/null

# ===清理上次导出的数据===

COUNT=`ls $TMP_DIR | wc -w`
if [ $COUNT -ne 0 ]; then
    rm -f $TMP_DIR/*.sql
fi

# ===清理历史归档文件===

find $BAK_DIR/*.tar.gz -type f -ctime +$BAK_KEEPTIME | xargs rm -f

# ===统计备份信息===

# 获取当前备份大小
BAK_SIZE=`ls -lh $BAK_DIR/$BAK_FILE | awk '{print $5}'`

# 获取备份归档的总数量
ARCHIVES_NUM=`ls $BAK_DIR | grep -v tmp | wc -w`

# 获取所有归档占用的磁盘空间
ARCHIVES_SIZE=`du -sh $BAK_DIR | awk '{print $1}'`

# 输出统计信息
echo "\
数据库名：$DB_NAME
所在主机：$DB_HOST
备份时间：$BAK_TIME
备份文件：$BAK_DIR/$BAK_FILE
备份大小：$BAK_SIZE
归档数量：$ARCHIVES_NUM
占用空间：$ARCHIVES_SIZE
备份主机：$(hostname)
主机地址：$(hostname -i) \
"

# ===脚本结束===
