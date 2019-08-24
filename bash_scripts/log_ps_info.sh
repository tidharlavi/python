#!/bin/bash

FILE=/home/eliad/python/image_crawler/logs/ps_info.log

if [ ! -f $FILE ]
then
    	touch $FILE
fi
	
while true; 
do 
	PSDATA=`ps aux | sort -rn -k 5,6`
	
	echo "=========================================================================== $(date)" >> $FILE
	echo "$PSDATA)" >> $FILE

	sleep 600
done
