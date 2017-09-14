
#!/bin/sh

source /etc/profile

cd `dirname $0`



# last day
#statdate=`date '+%Y%m%d' -d "-1 days"`

# the day
statdate=`date '+%Y%m%d'`

statdate="20170430"

echo $statdate 


nohup /usr/local/python2.7/bin/python -u sync_folder_to_mysql.py ../../supplier/ret/data/$statdate >> ${statdate}.log 2>&1 &


#nohup /usr/local/python2.7/bin/python -u sync_folder_to_mysql.py /home/tangpingfeng/result/supplier/ret/data/$statdate >> ${statdate}.log 2>&1 &


