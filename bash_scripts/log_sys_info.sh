#!/bin/bash

FILE=/home/eliad/python/image_crawler/logs/sys_info.log
while true; 
do 
	MEMDATA=`sudo cat /proc/meminfo | egrep "^(MemTotal|MemFree|Cached)" | sed 's/[^0-9]\+//g' | tr '\n' '\t'`
	CPUDATA=`sudo cat /proc/loadavg | sed 's/ .\+//'`

	if [ ! -f $FILE ]
	then
        	echo "Date      MemTotal        MemFree MemCached       CPU-usage" > $FILE
	fi
	echo "$(date)   $MEMDATA        $CPUDATA" >> $FILE

	sleep 5
done
