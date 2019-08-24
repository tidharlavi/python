#!/bin/bash

# Conf
IMAGE_CRAWLER_SRC_FOLDER="/home/eliad/git/python/image_crawler_prj/src"
GIT_BASH_FOLDER="/home/eliad/git/bash"

echo "Start flower (celery stats on http://localhost:5555)"
cd $IMAGE_CRAWLER_SRC_FOLDER; 
celery -A task_queue flower &

echo "Start log system info './log_sys_info.sh &'"
cd $GIT_BASH_FOLDER
#./log_sys_info.sh &

echo "Start worker"
cd $IMAGE_CRAWLER_SRC_FOLDER; 
celery -A task_queue worker -l info -f ~/python/image_crawler/logs/celery.log &

echo "Start Image Crawler"
cd $IMAGE_CRAWLER_SRC_FOLDER; 
python image_crawler.py
