'''
Created on Dec 20, 2017

@author: eliad
'''

# celery
from __future__ import absolute_import, unicode_literals
from .celery import app
from celery.utils.log import get_task_logger

# general
import os
import logging
import json

# tasks
import extractor
import loader
import crawler

# locals
import object_model

celery_log = get_task_logger(__name__)

@app.task
def extract_load_crawl(url_info_dic):
    celery_log.info('task extract_load_crawl'.format())
    
    url_info = object_model.url_info.UrlInfo(url_info_dic)
    
    celery_log.info(', '.join("%s: %s" % url_info for url_info in vars(url_info).items()))
    
    ldr =  loader.Loader()

    ext = extractor.extractor({
                               "dest_folder": "/home/eliad/python/image_crawler/images_db"
    })
    
    celery_log.info('Going to ext.extract_info(url_info)')
    ext.extract_info(url_info)
    print("Statistics extractor: '"+json.dumps(ext.stats.Get())+"'.")
    
    if url_info.initiator_type == object_model.url_info.UrlInfoInitiatorTypeEnum.image:
        celery_log.info('Initiated by Image (image link).')
        # Add page information to image - keywords
        ldr.update_metadata(url_info, ext)
    elif url_info.initiator_type == object_model.url_info.UrlInfoInitiatorTypeEnum.search:
        celery_log.info('Going to Initiated by Search.')
        # Add page information to image search information - check if the same image exist in the link, add keywords
    
    # Go over extract images and add them to image
    celery_log.info('Going to: ldr.load_image_details_array().')
    ldr.load_image_details_array(ext.image_details_arr)
    print("Statistics loader: '"+json.dumps(ldr.stats.Get())+"'.")

    # Add internal links to taskq 
    crlr = crawler.Crawler({})
    celery_log.info('Going to: crlr.update_url_extract_info().')
    crlr.update_url_extract_info(url_info)
    
    celery_log.info('Going to: crlr.insert_urls().')
    crlr.insert_urls(ext.internal_links)
    print("Statistics crawler: '"+json.dumps(crlr.stats.Get())+"'.")
    
    celery_log.info('1going to: crlr.insert_urls().')
    crlr.insert_urls(ext.image_links)
    print("Statistics crawler: '"+json.dumps(crlr.stats.Get())+"'.")
    
    
    





     