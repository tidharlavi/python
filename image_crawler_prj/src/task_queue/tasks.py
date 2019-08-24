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
import common
import config

# Crawler stats
from elasticsearch import Elasticsearch
from datetime import datetime

celery_log = get_task_logger(__name__)

@app.task
def extract_load_crawl(url_info_dic):
    celery_log.info('task extract_load_crawl()')
    
    stats = common.Stats()
    
    url_info = object_model.url_info.UrlInfo(url_info_dic)
    
    stats.Add("crwlr_id", url_info.crwl_curr)
    stats.Add("crwlr_url", url_info.url)
    stats.Add("datetime", datetime.now())
    
    celery_log.info(', '.join("%s: %s" % url_info for url_info in vars(url_info).items()))
    
    ldr =  loader.Loader()

    ext = extractor.extractor({ "dest_folder": config.conf["OUTPUT_FOLDER"] })
    
    celery_log.info('Going to ext.extract_info(url_info)')
    res = ext.extract_info(url_info)
    celery_log.info("Statistics extractor: '%s'.", ext.stats.Print(pretty=False))
    if not res:
        celery_log.info('Fail to ext.extract_info(url_info), return Task.')
        return
    
    stats.add_stats(ext.stats, "ext")
    
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
    celery_log.info("Statistics loader: '%s'.", ldr.stats.Print(pretty=False))
    stats.add_stats(ldr.stats, "ldr")

    crlr = crawler.Crawler({})
    celery_log.info('Going to: crlr.update_url_extract_info().')
    crlr.update_url_extract_info(ext, url_info)
    
    # Add internal links to taskq
    if url_info.initiator_type != object_model.url_info.UrlInfoInitiatorTypeEnum.image: 
        celery_log.info('Going to: crlr.insert_urls(ext.image_links).')
        crlr.insert_urls(ext.internal_links)
        celery_log.info("Statistics crawler internal_links: '%s'.", crlr.stats.Print(pretty=False))
        stats.add_stats(crlr.stats, "crlr_links")
        
        celery_log.info('Going to: crlr.insert_urls(ext.image_links).')
        crlr.insert_urls(ext.image_links)
        celery_log.info("Statistics crawler image_links: '%s'.", crlr.stats.Print(pretty=False))
        stats.add_stats(crlr.stats, "crlr_image_links")
    
    celery_log.info('Going to: update crwl statistics')
    ES_CRWLR_STATS_INDEX = "crwlr_stats"
    ES_CRWLR_STATS_DOC_TYPE = 'crwlr_stat'
    es = Elasticsearch()
    if not es.indices.exists(index=ES_CRWLR_STATS_INDEX):
        es.indices.create(index=ES_CRWLR_STATS_INDEX)
    
    rec = stats.Get()
    rec_id = url_info.crwl_curr + "_" + url_info._id
    es.index(index=ES_CRWLR_STATS_INDEX, doc_type=ES_CRWLR_STATS_DOC_TYPE, body=rec, id=rec_id)
    





     