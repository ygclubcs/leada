#! /bin/bash
log_path=`pwd`
log_path=`dirname $log_path`
log_path=$log_path"/log/api.log"
disk_use_percent=`df -h | awk '{print $5 }' |  sed -n 2p | awk -F '%' '{print $1}'`
echo $disk_use_percent
if [ $disk_use_percent -ge 85 ]; then
   echo "" > $log_path
fi
echo $log_path
disk_use_percent=`df -h | awk '{print $5 }' |  sed -n 2p | awk -F '%' '{print $1}'`
echo $disk_use_percent
