#!/bin/bash

# Conf
IMAGE_CRAWLER_DATA_FOLDER="/home/eliad/python/image_crawler"
IMAGE_CRAWLER_SRC_FOLDER="/home/eliad/git/python/image_crawler_prj/src"

echo "Delete all data from '$IMAGE_CRAWLER_DATA_FOLDER'."
rm -fr $IMAGE_CRAWLER_DATA_FOLDER/images_sig_db/*
rm -fr $IMAGE_CRAWLER_DATA_FOLDER/images_db/*
rm -fr $IMAGE_CRAWLER_DATA_FOLDER/logs/*

echo "Kill all celery workers"
pkill -9 -f 'celery'

echo "Purge all celery tasks"
cd $IMAGE_CRAWLER_SRC_FOLDER; celery -A task_queue purge

echo "Delete local ES 'images' and 'crwlr_stats' index: 'DELETE /images' ..."
curl -XDELETE 'localhost:9200/images'
curl -XDELETE 'localhost:9200/crwlr_stats'

COMMAND="mongo urls --eval 'db.urls.drop()'"
echo "Drop urls mongo DB using: '$COMMAND'."
$COMMAND


